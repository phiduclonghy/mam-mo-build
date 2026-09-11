"""Archive and export a signed IPA on macOS, using an installed Apple identity."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,plistlib,re,shutil,subprocess,sys,tempfile,zipfile
ROOT=Path(__file__).resolve().parent

def run(*args):
    subprocess.run([str(a) for a in args],cwd=ROOT,check=True)

def validate_config(config,profile):
    team=config.get('team_id','');bundle=config.get('bundle_id','');method=config.get('method','release-testing')
    if not re.fullmatch(r'[A-Z0-9]{10}',team):raise ValueError('team_id cần là Apple Team ID thật, gồm 10 ký tự.')
    if not re.fullmatch(r'[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+',bundle):raise ValueError('bundle_id không hợp lệ.')
    if method not in ['release-testing','debugging','app-store-connect']:raise ValueError('method cần là release-testing, debugging hoặc app-store-connect.')
    if team not in profile.get('TeamIdentifier',[]):raise ValueError('Provisioning profile không thuộc Team ID đã chọn.')
    ent=profile.get('Entitlements',{});app_id=ent.get('application-identifier','');prefix=app_id.split('.',1)[0];pattern=app_id.split('.',1)[-1]
    if prefix not in profile.get('ApplicationIdentifierPrefix',[]):raise ValueError('Application identifier prefix của profile không hợp lệ.')
    if not (pattern==bundle or pattern.endswith('*') and bundle.startswith(pattern[:-1])):raise ValueError('Provisioning profile không khớp bundle_id.')
    expiry=profile.get('ExpirationDate')
    if not isinstance(expiry,datetime.datetime) or expiry.replace(tzinfo=datetime.timezone.utc)<=datetime.datetime.now(datetime.timezone.utc):raise ValueError('Provisioning profile đã hết hạn hoặc thiếu ngày hết hạn.')
    if method in ['release-testing','debugging'] and not profile.get('ProvisionedDevices'):raise ValueError('Profile cần chứa UDID của iPhone được phép cài.')
    if method=='debugging' and not ent.get('get-task-allow'):raise ValueError('Chế độ debugging cần profile Development.')
    if method!='debugging' and ent.get('get-task-allow'):raise ValueError('Chế độ phân phối cần profile Distribution.')
    if method=='app-store-connect' and profile.get('ProvisionedDevices'):raise ValueError('App Store Connect cần profile App Store, không dùng Ad Hoc/Development.')
    if not re.fullmatch(r'[A-Fa-f0-9-]{36}',profile.get('UUID','')):raise ValueError('UUID của profile không hợp lệ.')
    return team,bundle,method

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'signing.json')
    parser.add_argument('--profile',type=Path,default=ROOT/'profile.mobileprovision')
    args=parser.parse_args()
    if sys.platform!='darwin' or not shutil.which('xcodebuild'):raise ValueError('Cần macOS và Xcode để tạo IPA. Chưa có IPA được tạo.')
    if not args.config.is_file():raise ValueError('Sao chép signing.example.json thành signing.json rồi điền Team ID/bundle ID.')
    if not args.profile.is_file():raise ValueError('Thiếu profile.mobileprovision. Xuất provisioning profile từ tài khoản Apple của bạn.')
    config=json.loads(args.config.read_text())
    decoded=subprocess.check_output(['security','cms','-D','-i',str(args.profile.resolve())])
    profile=plistlib.loads(decoded);team,bundle,method=validate_config(config,profile)
    identity='Apple Development' if method=='debugging' else 'Apple Distribution'
    identities=subprocess.check_output(['security','find-identity','-v','-p','codesigning'],text=True)
    if identity not in identities:raise ValueError(f'Chưa có chứng chỉ {identity} và private key trong Keychain. Import file .p12 của bạn trước.')
    for folder in [Path.home()/'Library/MobileDevice/Provisioning Profiles',Path.home()/'Library/Developer/Xcode/UserData/Provisioning Profiles']:
        folder.mkdir(parents=True,exist_ok=True);shutil.copyfile(args.profile,folder/(profile['UUID']+'.mobileprovision'))
    output=ROOT/'build/iphone';output.mkdir(parents=True,exist_ok=True)
    archive=output/'MamMo.xcarchive';export=output/'export'
    if archive.exists():shutil.rmtree(archive)
    if export.exists():shutil.rmtree(export)
    options=output/'ExportOptions.plist'
    options.write_bytes(plistlib.dumps({'method':method,'teamID':team,'signingStyle':'manual','signingCertificate':identity,'provisioningProfiles':{bundle:profile['UUID']},'destination':'export','manageAppVersionAndBuildNumber':False}))
    run('xcodebuild','-project','MamMo.xcodeproj','-scheme','MamMo','-configuration','Release','-destination','generic/platform=iOS','-archivePath',archive,'archive',f'DEVELOPMENT_TEAM={team}',f'PRODUCT_BUNDLE_IDENTIFIER={bundle}','CODE_SIGN_STYLE=Manual',f'CODE_SIGN_IDENTITY={identity}',f'PROVISIONING_PROFILE_SPECIFIER={profile["UUID"]}')
    run('xcodebuild','-exportArchive','-archivePath',archive,'-exportPath',export,'-exportOptionsPlist',options)
    files=list(export.glob('*.ipa'))
    if len(files)!=1:raise ValueError('Xcode chưa xuất đúng một IPA. Xem log build/iphone.')
    with zipfile.ZipFile(files[0]) as z:
        if z.testzip() or not any(n.endswith('.app/embedded.mobileprovision') for n in z.namelist()):raise ValueError('IPA thiếu provisioning profile hoặc hỏng.')
        app_names=[n for n in z.namelist() if n.startswith('Payload/') and n.endswith('.app/Info.plist')]
        if len(app_names)!=1:raise ValueError('IPA không có cấu trúc ứng dụng hợp lệ.')
    with tempfile.TemporaryDirectory(prefix='mammo-ipa-verify-') as folder:
        with zipfile.ZipFile(files[0]) as z:z.extractall(folder)
        apps=list((Path(folder)/'Payload').glob('*.app'))
        if len(apps)!=1:raise ValueError('IPA cần chứa đúng một ứng dụng.')
        run('codesign','--verify','--deep','--strict',apps[0])
    final=ROOT/'Mam-Mo-iPhone.ipa';shutil.copyfile(files[0],final)
    final.with_suffix('.ipa.sha256').write_text(hashlib.sha256(final.read_bytes()).hexdigest()+'  '+final.name+'\n')
    print('Đã xuất IPA có chữ ký:',final)
    if method=='app-store-connect':print('Bản này dùng để gửi App Store Connect/TestFlight, không cài trực tiếp bằng Files.')
    else:print('Chỉ cài trên các iPhone có UDID trong profile, qua Xcode/Apple Configurator hoặc phương thức phân phối hợp lệ.')

if __name__=='__main__':
    try:main()
    except (ValueError,subprocess.CalledProcessError,OSError) as e:sys.exit(str(e))
