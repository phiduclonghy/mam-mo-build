"""Build a debug APK from an installed Android SDK, without downloading Gradle."""
from pathlib import Path
import os,sys,subprocess,shutil,zipfile
root=Path(__file__).resolve().parent
# Prefer an existing JDK or Android Studio's bundled JBR. Never download silently.
java_candidates=[Path(os.environ[k]) for k in ['JAVA_HOME','JDK_HOME'] if os.environ.get(k)]
if os.name=='nt':
 java_candidates += [Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Android/Android Studio/jbr',Path.home()/'AppData/Local/Programs/Android Studio/jbr']
elif sys.platform=='darwin':java_candidates += [Path('/Applications/Android Studio.app/Contents/jbr/Contents/Home')]
for candidate in java_candidates:
 if (candidate/'bin'/('javac.exe' if os.name=='nt' else 'javac')).is_file():
  os.environ['JAVA_HOME']=str(candidate);os.environ['PATH']=str(candidate/'bin')+os.pathsep+os.environ.get('PATH','');break
sdk=Path(os.environ.get('ANDROID_SDK_ROOT') or os.environ.get('ANDROID_HOME') or (Path.home()/'AppData/Local/Android/Sdk' if os.name=='nt' else Path.home()/'Library/Android/sdk' if sys.platform=='darwin' else Path.home()/'Android/Sdk'))
platform=sdk/'platforms/android-35/android.jar'
build_tools=sdk/'build-tools'
if not platform.exists() or not build_tools.exists():sys.exit('Chưa có Android SDK 35/build-tools. Cài qua Android Studio > SDK Manager rồi chạy lại. Không có APK được tạo.')
versions=sorted([p for p in build_tools.iterdir() if p.is_dir()],key=lambda p:tuple(int(x) if x.isdigit() else 0 for x in p.name.split('.')))
if not versions:sys.exit('Chưa có Android SDK Build-tools.')
tools=next((p for p in versions if p.name=='35.0.1'),versions[-1])
def tool(name):
 for suffix in ('.exe','.bat','') if os.name=='nt' else ('',):
  if (tools/(name+suffix)).exists():return str(tools/(name+suffix))
 raise SystemExit('Missing build tool '+name)
def run(*args):subprocess.run([str(a) for a in args],cwd=root,check=True)
for command in ('javac','keytool'):
 if not shutil.which(command):sys.exit('Cần JDK 17 với '+command+' trong PATH.')
out=root/'build/manual';out.mkdir(parents=True,exist_ok=True)
gen=out/'gen';classes=out/'classes';dex=out/'dex'
for p in (gen,classes,dex):
 if p.exists():shutil.rmtree(p)
 p.mkdir()
run(tool('aapt2'),'compile','--dir',root/'app/src/main/res','-o',out/'resources.zip')
run(tool('aapt2'),'link','-o',out/'unsigned.apk','-I',platform,'--manifest',root/'app/src/main/AndroidManifest.xml','--java',gen,'--min-sdk-version','23','--target-sdk-version','35','--version-code','3','--version-name','3.0.0','-A',root/'app/src/main/assets',out/'resources.zip')
sources=list((root/'app/src/main/java').rglob('*.java'))+list(gen.rglob('*.java'))
run('javac','-encoding','UTF-8','-source','8','-target','8','-classpath',platform,'-d',classes,*sources)
run(tool('d8'),'--min-api','23','--lib',platform,'--output',dex,*classes.rglob('*.class'))
with zipfile.ZipFile(out/'unsigned.apk','a',zipfile.ZIP_DEFLATED) as archive:
 for file in dex.glob('*.dex'):archive.write(file,file.name)
run(tool('zipalign'),'-f','-p','4',out/'unsigned.apk',out/'aligned.apk')
keystore=out/'debug.keystore'
if not keystore.exists():run('keytool','-genkeypair','-keystore',keystore,'-storepass','android','-keypass','android','-alias','androiddebugkey','-dname','CN=Android Debug,O=Android,C=US','-keyalg','RSA','-keysize','2048','-validity','10000')
apk=root/'Mam-Mo-Android-debug.apk'
run(tool('apksigner'),'sign','--ks',keystore,'--ks-pass','pass:android','--key-pass','pass:android','--out',apk,out/'aligned.apk')
run(tool('apksigner'),'verify','--verbose',apk)
run(tool('zipalign'),'-c','4',apk)
with zipfile.ZipFile(apk) as archive:
 required={'AndroidManifest.xml','classes.dex','assets/web/index.html','assets/web/audio.js','assets/web/data/catalog.json'}
 if not required.issubset(archive.namelist()) or archive.testzip():sys.exit('APK thiếu nội dung hoặc bị lỗi.')
import hashlib
(root/'Mam-Mo-Android-debug.apk.sha256').write_text(hashlib.sha256(apk.read_bytes()).hexdigest()+'  '+apk.name+'\n',encoding='utf-8')
print('APK ký debug để thử trên thiết bị:',apk)
