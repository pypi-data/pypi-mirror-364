import unittest
import random
import os
from pybmdope.bmdope import BMDOPE

class TestBMDOPE(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None  # Allow full diff output
        self.key = BMDOPE.generate_key()
        self.bmdope = BMDOPE(self.key)

    def test_plaintext_equals_decrypt(self):
        """Tests if the decrypted data matches the original plaintext."""
        data1 = b"apple"
        data2 = b"banana"
        data3 = b"cherry"

        encrypted1 = self.bmdope.encrypt(data1)
        encrypted2 = self.bmdope.encrypt(data2)
        encrypted3 = self.bmdope.encrypt(data3)

        decrypted1 = self.bmdope.decrypt(encrypted1)
        decrypted2 = self.bmdope.decrypt(encrypted2)
        decrypted3 = self.bmdope.decrypt(encrypted3)

        # Ensure decrypted data matches original plaintext
        self.assertEqual(decrypted1, data1)
        self.assertEqual(decrypted2, data2)
        self.assertEqual(decrypted3, data3)

    def test_order_preserving_property_with_bytes(self):
        """Tests if the lexicographical order of byte strings is preserved using encrypt method."""
        data1 = b"apple"
        data2 = b"banana"
        data3 = b"cherry"

        # Pre-condition: data1 < data2 < data3
        self.assertTrue(data1 < data2 < data3)

        encrypted1 = self.bmdope.encrypt(data1)
        encrypted2 = self.bmdope.encrypt(data2)
        encrypted3 = self.bmdope.encrypt(data3)

        # Post-condition: encrypted(data1) < encrypted(data2) < encrypted(data3)
        self.assertTrue(encrypted1 < encrypted2 < encrypted3)

    def test_order_preserving_property_with_numbers(self):
        """Tests if the order of numbers (converted to bytes) is preserved using encrypt method."""
        num1 = (100).to_bytes(8, 'big')
        num2 = (2000).to_bytes(8, 'big')
        num3 = (30000).to_bytes(8, 'big')

        # Pre-condition: num1 < num2 < num3
        self.assertTrue(num1 < num2 < num3)

        encrypted1 = self.bmdope.encrypt(num1)
        encrypted2 = self.bmdope.encrypt(num2)
        encrypted3 = self.bmdope.encrypt(num3)

        # Post-condition: encrypted(num1) < encrypted(num2) < encrypted(num3)
        self.assertTrue(encrypted1 < encrypted2 < encrypted3)

    def test_decrypt_order_preserving_property_with_bytes(self):
        """Tests if the lexicographical order of byte strings is preserved after decryption."""
        data1 = b"apple"
        data2 = b"banana"
        data3 = b"cherry"

        encrypted1 = self.bmdope.encrypt(data1)
        encrypted2 = self.bmdope.encrypt(data2)
        encrypted3 = self.bmdope.encrypt(data3)

        decrypted1 = self.bmdope.decrypt(encrypted1)
        decrypted2 = self.bmdope.decrypt(encrypted2)
        decrypted3 = self.bmdope.decrypt(encrypted3)

        # Post-condition: decrypted(data1) < decrypted(data2) < decrypted(data3)
        self.assertTrue(decrypted1 < decrypted2 < decrypted3)
        self.assertEqual(decrypted1, data1)
        self.assertEqual(decrypted2, data2)
        self.assertEqual(decrypted3, data3)

    def test_decrypt_order_preserving_property_with_numbers(self):
        """Tests if the order of numbers (converted to bytes) is preserved after decryption."""
        num1 = (100).to_bytes(8, 'big')
        num2 = (2000).to_bytes(8, 'big')
        num3 = (30000).to_bytes(8, 'big')

        encrypted1 = self.bmdope.encrypt(num1)
        encrypted2 = self.bmdope.encrypt(num2)
        encrypted3 = self.bmdope.encrypt(num3)

        decrypted1 = self.bmdope.decrypt(encrypted1)
        decrypted2 = self.bmdope.decrypt(encrypted2)
        decrypted3 = self.bmdope.decrypt(encrypted3)
        
        # Pad the decrypted values to ensure they are comparable
        decrypted1 = decrypted1.rjust(8, b'\x00')
        decrypted2 = decrypted2.rjust(8, b'\x00')
        decrypted3 = decrypted3.rjust(8, b'\x00')

        # Post-condition: decrypted(num1) < decrypted(num2) < decrypted(num3)
        self.assertEqual(decrypted1, num1)
        self.assertEqual(decrypted2, num2)
        self.assertEqual(decrypted3, num3)
        self.assertTrue(decrypted1 < decrypted2 < decrypted3)

    def test_order_preserving_property_with_large_random_numbers(self):
        """Tests if BMDOPE preserves order for a sorted list of large random numbers."""
        random_numbers = [random.randint(1, 10**18).to_bytes(8, 'big') for _ in range(2)]
        sorted_numbers = sorted(random_numbers)

        encrypted_numbers = [self.bmdope.encrypt(num) for num in sorted_numbers]

        # Ensure encrypted numbers are also sorted
        self.assertTrue(all(encrypted_numbers[i] < encrypted_numbers[i + 1] for i in range(len(encrypted_numbers) - 1)))
    
    def test_random_large_quantity_of_data(self):
        """Tests if BMDOPE can handle a large quantity of random data and preserves order."""
        data = []
        while len(data) < 1000:
            num = random.randint(0, 65535).to_bytes(2, 'big')
            if num not in data:
                data.append(num)
            
        data = sorted(data)
        encrypted_data = [self.bmdope.encrypt(d) for d in data]
        encrypted_data_int = [int.from_bytes(ed, 'big') for ed in encrypted_data]
        
        self.assertEqual(encrypted_data_int, sorted(encrypted_data_int))
        
    def test_bound(self):
        """Tests if the encrypt_bound method correctly handles bounds."""
        data = random.randint(1, 10**18).to_bytes(8, 'big')
        encrypted_data = self.bmdope.encrypt(data)
        lower_bound, upper_bound = self.bmdope.encrypt_bound(data)

        # Check if the bounds are valid encrypted data
        self.assertTrue(isinstance(lower_bound, bytes))
        self.assertTrue(isinstance(upper_bound, bytes))
        
        # Check if lower bound is less than or equal to upper bound
        lower_bound_int = int.from_bytes(lower_bound, 'big')
        upper_bound_int = int.from_bytes(upper_bound, 'big')
        self.assertLessEqual(lower_bound_int, upper_bound_int)
        
        # Check if the encrypted data is within the bounds
        encrypted_data_int = int.from_bytes(encrypted_data, 'big')
        self.assertGreaterEqual(encrypted_data_int, lower_bound_int)
        self.assertLessEqual(encrypted_data_int, upper_bound_int)
        
        # Check if data - 1 is not within the bounds
        data_minus_one = (int.from_bytes(data, 'big') - 1).to_bytes(8, 'big')
        encrypted_data_minus_one = self.bmdope.encrypt(data_minus_one)
        encrypted_data_minus_one_int = int.from_bytes(encrypted_data_minus_one, 'big')
        self.assertLess(encrypted_data_minus_one_int, lower_bound_int)

if __name__ == "__main__":
    unittest.main()
