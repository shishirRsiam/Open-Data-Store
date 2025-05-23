import time  # Import the time module to measure execution time

# Start timing the OTP generation process
start = time.time()

# Define a class named OTP to handle the generation and storage of OTPs
class OTP():
    def __init__(self):
        # Initialize two lists:
        # - one for storing all possible 4-digit OTPs
        # - another for all possible 6-digit OTPs
        self.four_digit_otp = []
        self.six_digit_otp = []

    # Recursive function to generate all possible 4-digit OTPs
    def genarate_four_digit_otp(self, cur, visited):
        # Base case: if the current string has 4 digits, add it to the list
        if len(cur) == 4:
            self.four_digit_otp.append(cur)
            return ""
        
        # If the current state (length and current string) is already visited, skip it
        if (len(cur), cur) in visited:
            return visited[(len(cur), cur)]
        
        # Try appending digits 0-9 to the current string
        for i in range(10):
            otp = self.genarate_four_digit_otp(cur + str(i), visited)

        # Mark the current state as visited (for memoization)
        visited[(len(cur), cur)] = otp
        return otp

    # Recursive function to generate all possible 6-digit OTPs
    def genarate_six_digit_otp(self, cur, visited):
        # Base case: if the current string has 6 digits, add it to the list
        if len(cur) == 6:
            self.six_digit_otp.append(cur)
            return ""
        
        # If the current state (length and current string) is already visited, skip it
        if (len(cur), cur) in visited:
            return visited[(len(cur), cur)]
        
        # Try appending digits 0-9 to the current string
        for i in range(10):
            otp = self.genarate_six_digit_otp(cur + str(i), visited)

        # Mark the current state as visited (for memoization)
        visited[(len(cur), cur)] = otp
        return otp

    # Function to save a list of OTPs to a file
    def save_otp(self, file_name, otps):
        n = len(otps)  # Get the total number of OTPs
        file = open(file_name, "w")  # Open the file in write mode
        file.write("[")  # Begin writing a list representation
        for index in range(n):
            file.write(f"{otps[index]}")  # Write the OTP
            if index < n - 1:
                file.write(", ")  # Add comma and space except after the last item
        file.write("]")  # End of list
        file.close()  # Close the file

# Create an instance of the OTP class
otp = OTP()

# Generate all 4-digit OTPs (0000 to 9999)
otp.genarate_four_digit_otp("", {})

# Generate all 6-digit OTPs (000000 to 999999)
otp.genarate_six_digit_otp("", {})

# Save the 4-digit OTPs to a file
otp.save_otp("01_4_Digits_OTP.txt", otp.four_digit_otp)

# Save the 6-digit OTPs to a file
otp.save_otp("01_6_Digits_OTP.txt", otp.six_digit_otp)

# End timing
end = time.time()

# Display a summary and confirmation message
print(f"✅ OTP generation finished in {end - start:.2f} seconds.\n")
print("🎉 Success! OTPs generated and stored:")
print("📁 01_4_Digits_OTP.txt — 10,000 4-digit OTPs")
print("📁 01_6_Digits_OTP.txt — 1,000,000 6-digit OTPs")
