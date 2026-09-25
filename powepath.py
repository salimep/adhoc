def extract_powermt_data(file_path):
    device_dict = {}
    
    # Temporary variables to hold data as we parse
    current_pseudo = None
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Extract Pseudo name
            if line.startswith("Pseudo name="):
                current_pseudo = line.split("=")[1].strip()
                
            # Extract Device WWN
            elif line.startswith("Device WWN="):
                wwn_value = line.split("=")[1].strip()
                
                # If we have a matching Pseudo name, save it to the dictionary
                if current_pseudo:
                    device_dict[current_pseudo] = wwn_value
                    # Reset current_pseudo for the next block
                    current_pseudo = None

    return device_dict

# --- Execution ---
# Replace 'powermt_output.txt' with the actual path to your file
file_name = '/Users/mac/Downloads/WWPN_DR1_After_Upgrade.txt' 
after_upgrade = extract_powermt_data(file_name)


file_name = '/Users/mac/Downloads/powermt_display_DR1.txt'
before_upgrade = extract_powermt_data(file_name)

def compare_dictionaries(dict1, dict2):
    print(f"{'Key':<15} | {'Dict 1 Value':<20} | {'Dict 2 Value':<20}")
    print("-" * 62)
    
    # Find keys that exist in both dictionaries
    common_keys = set(dict1.keys()) & set(dict2.keys())
    
    has_differences = False
    for key in common_keys:
        # Check if the values are different
        if dict1[key] != dict2[key]:
            print(f"{key:<15} | {str(dict1[key]):<20} | {str(dict2[key]):<20}")
            has_differences = True
            
    if not has_differences:
        print("All matching keys have identical values!")

# --- Example Usage ---

#print("Dict 2 Before Fix:", dict2)

# --- The Key Swapping Logic ---
# 2. Build the corrected Dict 2

dict2_corrected = {}

for correct_key, wwn_value in before_upgrade.items():
    # Check if this WWN value exists anywhere in Dict 2
    for wrong_key,wrong_value in after_upgrade.items():
        if wwn_value == wwn_value:
           # print (wwn_value)
            dict2_corrected[correct_key] = wrong_key



for a,b in before_upgrade.items():
    for c,d in after_upgrade.items():
        if b == d and a != c:
            #print (b,d,end=" ")
            print (a,c,end=",")
    #if before_upgrade[a] == '60000970000297200043533030374233':
        
            #print("\nDict 2 After Fix :", dict2_corrected)


#print("\nDict 2 After Fix :", dict2_corrected)