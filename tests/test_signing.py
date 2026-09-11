import unittest,importlib.util,datetime,copy
from pathlib import Path
spec=importlib.util.spec_from_file_location('build_ipa',Path(__file__).resolve().parents[1]/'iOS/build_ipa.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class SigningValidation(unittest.TestCase):
    def setUp(self):
        self.config={'team_id':'ABCDEFGHIJ','bundle_id':'com.mammo.reader','method':'release-testing'}
        self.profile={'UUID':'abcdefab-1234-1234-1234-abcdefabcdef','TeamIdentifier':['ABCDEFGHIJ'],'ApplicationIdentifierPrefix':['ABCDEFGHIJ'],'Entitlements':{'application-identifier':'ABCDEFGHIJ.com.mammo.reader','get-task-allow':False},'ExpirationDate':datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(days=30),'ProvisionedDevices':['test-device-udid']}
    def test_matching_profile(self):self.assertEqual(module.validate_config(self.config,self.profile),('ABCDEFGHIJ','com.mammo.reader','release-testing'))
    def test_other_team(self):
        self.config['team_id']='KLMNOPQRST'
        with self.assertRaises(ValueError):module.validate_config(self.config,self.profile)
    def test_other_app(self):
        self.config['bundle_id']='com.other.app'
        with self.assertRaises(ValueError):module.validate_config(self.config,self.profile)
    def test_expired_profile(self):
        self.profile['ExpirationDate']=datetime.datetime(2000,1,1)
        with self.assertRaises(ValueError):module.validate_config(self.config,self.profile)
    def test_no_registered_devices(self):
        self.profile.pop('ProvisionedDevices')
        with self.assertRaises(ValueError):module.validate_config(self.config,self.profile)
    def test_wrong_identity_type(self):
        self.profile['Entitlements']['get-task-allow']=True
        with self.assertRaises(ValueError):module.validate_config(self.config,self.profile)
    def test_wildcard_profile(self):
        self.profile['Entitlements']['application-identifier']='ABCDEFGHIJ.com.mammo.*'
        self.assertEqual(module.validate_config(self.config,self.profile)[1],'com.mammo.reader')
    def test_invalid_example_config(self):
        self.config['team_id']='YOUR_APPLE_TEAM_ID'
        with self.assertRaises(ValueError):module.validate_config(self.config,self.profile)
if __name__=='__main__':unittest.main()
