from cacao_password_generator.core import generate
from cacao_password_generator.rating import rating, detailed_rating

password = generate(length=20)
strength_rating = rating(password)
detailed_analysis = detailed_rating(password)

print(f"Password: {password}")
print(f"Strength: {strength_rating}")
print(f"Entropy: {detailed_analysis['entropy']:.2f} bits")
print(f"Character Space: {detailed_analysis['character_set_size']}")
print(f"Estimated Crack Time: {detailed_analysis['crack_time_formatted']}")