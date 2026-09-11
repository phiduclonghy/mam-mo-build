"""Import/clean Apple signing inputs supplied as GitHub Actions secrets; never log them."""
from pathlib import Path
import base64,json,os,plistlib,secrets,shutil,subprocess,sys
TEMP=Path(os.environ.get('RUNNER_TEMP','/tmp'))/'mammo-signing'

def run(*args):subprocess.run(list(args),check=True,stdout=subprocess.DEVNULL)

def cleanup():
    keychain=TEMP/'build.keychain-db'
    if keychain.exists():subprocess.run(['security','delete-keychain',str(keychain)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    decoded=TEMP/'profile.plist'
    if decoded.exists():
        uuid=plistlib.loads(decoded.read_bytes()).get('UUID','')
        if uuid:
            for directory in ['Library/MobileDevice/Provisioning Profiles','Library/Developer/Xcode/UserData/Provisioning Profiles']:(Path.home()/directory/(uuid+'.mobileprovision')).unlink(missing_ok=True)
    shutil.rmtree(TEMP,ignore_errors=True)

def setup():
    if sys.platform!='darwin':sys.exit('Apple signing requires a macOS runner.')
    required=['IOS_CERTIFICATE_P12_BASE64','IOS_CERTIFICATE_PASSWORD','IOS_PROFILE_BASE64','IOS_TEAM_ID','IOS_BUNDLE_ID']
    if any(not os.environ.get(k) for k in required):sys.exit('Thiếu GitHub Secrets cho chữ ký Apple. Xem README; không gửi private key trong chat.')
    TEMP.mkdir(mode=0o700,parents=True,exist_ok=True)
    certificate=TEMP/'certificate.p12';profile=TEMP/'profile.mobileprovision'
    certificate.write_bytes(base64.b64decode(os.environ['IOS_CERTIFICATE_P12_BASE64'],validate=True));profile.write_bytes(base64.b64decode(os.environ['IOS_PROFILE_BASE64'],validate=True))
    decoded=subprocess.check_output(['security','cms','-D','-i',str(profile)]);(TEMP/'profile.plist').write_bytes(decoded)
    config={'team_id':os.environ['IOS_TEAM_ID'],'bundle_id':os.environ['IOS_BUNDLE_ID'],'method':'release-testing'}
    (TEMP/'signing.json').write_text(json.dumps(config))
    password=secrets.token_urlsafe(30);keychain=str(TEMP/'build.keychain-db')
    run('security','create-keychain','-p',password,keychain)
    run('security','set-keychain-settings','-lut','3600',keychain)
    run('security','unlock-keychain','-p',password,keychain)
    run('security','import',str(certificate),'-P',os.environ['IOS_CERTIFICATE_PASSWORD'],'-A','-t','cert','-f','pkcs12','-k',keychain)
    run('security','set-key-partition-list','-S','apple-tool:,apple:','-k',password,keychain)
    run('security','list-keychains','-d','user','-s',keychain)
    certificate.unlink()
    print('Apple signing inputs imported into the temporary build keychain.')

if __name__=='__main__':
    try:cleanup() if '--cleanup' in sys.argv else setup()
    except Exception:sys.exit('Không chuẩn bị được chữ ký Apple. Kiểm tra certificate/profile và Secrets; giá trị bí mật không được in ra.')
