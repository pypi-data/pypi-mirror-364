import sys
import unittest

sys.path.append("./src")
from cryptanalysis_tools.crypto.hash import length_extension_attack


class TestLengthExtensionAttack(unittest.TestCase):
    def __init__(self, methodName: str = "TestLengthExtensionAttack") -> None:
        super().__init__(methodName)
        print(methodName)
        self.secret1 = b'secret1'
        self.secret2 = b'secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2secret2'

        self.message1 = b"hello world"
        self.message2 = b"hello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello worldhello world"
        

    def test_length_extension_attack(self):
        self.assertEqual(
            length_extension_attack.sm3_attack(len(self.secret1), bytes.fromhex("98451236f1ee211882d862b0a1e852c9432270db49f87e1403dcd4c7bc4c2e8f"), self.message1).hex(),
            "9944f2fc9e673c79fa77601744ccf859940ffd0cdf8a12c59351a56898cd81f2",
        )
        self.assertEqual(
            length_extension_attack.sm3_attack(len(self.secret1), bytes.fromhex("98451236f1ee211882d862b0a1e852c9432270db49f87e1403dcd4c7bc4c2e8f"), self.message2).hex(),
            "65b91fee4c236fcb5feb500441b33762d9c79924e6e7b43890ee958610e8cee2",
        )
        self.assertEqual(
            length_extension_attack.sm3_attack(len(self.secret2), bytes.fromhex("c821936e31d039ab70b6b7dc1cf3c6857dd5b36adeb6c0fc0e4e87c9346ce1ee"), self.message1).hex(),
            "c85fa362c91ac07cc4d9860c3d328aad1113e8fe40c2d5420b3389875692bd35",
        )
        self.assertEqual(
            length_extension_attack.sm3_attack(len(self.secret2), bytes.fromhex("c821936e31d039ab70b6b7dc1cf3c6857dd5b36adeb6c0fc0e4e87c9346ce1ee"), self.message2).hex(),
            "7970f1b118b3d41cea2a81b539df3255568c38ddd2c86902e79e9d4fc78d4fd4",
        )

        # crypto cup
        self.assertEqual(
            length_extension_attack.sm3_attack(36, bytes.fromhex("f4ce927c79b616e8e8f7223828794eedf9b16591ae572172572d51e135e0d21a"), bytes.fromhex("ffffffff")).hex(),
            "9ada25bef8d4f6eda5648400c5c5349b03ab69589ea637f4c21fb0ae8b0461cb",
        )
