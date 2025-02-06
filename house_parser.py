# native python libraries
from datetime import datetime
from urllib.request import Request, urlopen
from html.parser import HTMLParser
import time
import csv
import json

# external libraries (need pip install)
import validators
import pandas as pd

# NOTE: match-case conditionals only work for python >= 3.10, otherwise rewrite as if-else or install newer version
# will also need to pip install external libraries to newer version if not default

# Class definitions
class House():
    def __init__(self, url):
        self.url = url
        self.dict_essential_info = {
            "Price": None,
            "Bedrooms": None,
            "Bathrooms": None,
            "Full Baths": None,
            "Half Baths": None,
            "Square Footage": None,
            "Lot SQFT": None,
            "Year Built": None,
            "Type": None,
            "Sub-Type": None,
            "Style": None,
            "Status": None
        }
        self.dict_community_info = {
            "Address": None,
            "Subdivision": None,
            "City": None,
            "Province": None,
            "Postal Code": None
        }
        self.amenities = {
            "Parking Spaces": None,
            "Parking": None, 
            "# of Garages": None
        }
   
class HouseParser(HTMLParser):
    def __init__(self, url):
        super().__init__()
        self.House = House(url)
        self.current_tag = None
        self.current_data = []
        self.current_tag_id = None
        self.current_tag_class = None
        self.current_listing_section = None
        self.tag_to_parse = None
        self.class_to_parse = None
        self.previous_key = None
        self.dict_generic = None

    def handle_starttag(self, tag, attrs):
        if tag == "div":
            dict_attrs = dict(attrs)
            if "id" in dict_attrs:
                self.current_tag_id = dict_attrs["id"]
            if "class" in dict_attrs:
                self.current_tag_class = dict_attrs["class"]
                self.tag_to_parse = "h4"
        self.current_tag = tag
             
    def handle_data(self, data):
        if self.current_tag_id == "listing-body" and self.current_tag_class == "dataset":
            #print(f"class: {self.current_tag_class} tag: {self.current_tag}")
            
            # get data/current listing section
            self.current_data = data.strip()    
            if self.current_tag == "h4":
                self.current_listing_section = data.strip()
            
            # set generic dict based on current listing section
            match self.current_listing_section:
                case "Essential Information":
                    self.dict_generic = self.House.dict_essential_info
                case "Community Information":
                    self.dict_generic = self.House.dict_community_info
                case "Amenities":
                    self.dict_generic = self.House.amenities
                case _:
                    pass

            # if current_data is dict key, then next tag should have corresponding value
            # key/value pair defined by strong/span tag pairs within dataset class div
            if self.current_data in self.dict_generic:           
                self.previous_key = self.current_data
                pass 
            if self.previous_key in self.dict_generic:
                self.dict_generic[self.previous_key] = self.current_data

            # match generic dict back based on current section
            match self.current_listing_section:
                case "Essential Information":
                    self.House.dict_essential_info = self.dict_generic
                case "Community Information":
                    self.House.dict_community_info = self.dict_generic
                case "Amenities":
                    self.House.amenities = self.dict_generic
                case _:
                    pass
            
    def handle_endtag(self, tag):
        pass

# add/remove variables based on what you want/what's parsed
class HouseOutput():
    def __init__(self, house):
        self.url = house.url
        self.Address = house.dict_community_info["Address"]
        self.Subdivision = house.dict_community_info["Subdivision"]
        self.PostalCode = house.dict_community_info["Postal Code"]
        self.Price = house.dict_essential_info["Price"]
        self.Bedrooms = house.dict_essential_info["Bedrooms"]
        self.Bathrooms = house.dict_essential_info["Bathrooms"]
        self.FullBaths = house.dict_essential_info["Full Baths"]
        self.HalfBaths = house.dict_essential_info["Half Baths"]
        self.SquareFootage = house.dict_essential_info["Square Footage"]
        self.LotSQFT = house.dict_essential_info["Lot SQFT"]
        self.YearBuilt = house.dict_essential_info["Year Built"]
        self.Type = house.dict_essential_info["Type"]
        self.SubType = house.dict_essential_info["Sub-Type"]
        self.Style = house.dict_essential_info["Style"]
        self.ParkingSpaces = house.amenities["Parking Spaces"]
        self.Parking = house.amenities["Parking"]
        self.NumGarages = house.amenities["# of Garages"]
        #self.Status = house.dict_essential_info["Status"]


# Function Definitions
def get_html_page(str_url, bool_decode = True):
    #sleep in case of 503 error from too many requests
    #time.sleep(0.05)
    req = Request(str_url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req)
    return html.read().decode('utf-8') if bool_decode else html.read()

def output_house_list(int_output_format, list_houses, date_today):
    dict_output_format = {
        1: "csv",
        2: "xlsx",
        3: "json",
        4: "cli"
    }

    print(f"\nOutputting House list to {dict_output_format[int_output_format]}...") 
    if int_output_format in [1, 2, 3]:
        str_output_file = f"house_list_output_{date_today}.{dict_output_format[int_output_format]}"
   
    match int_output_format:
        case 1:
            with open(str_output_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(list_houses[0].__dict__.keys())
                for house in list_houses:
                    writer.writerow(house.__dict__.values())
            print(f"Output file: {str_output_file}")
        case 2:
            df_union = pd.DataFrame()
            for house in list_houses:
                df_house = pd.DataFrame(data=house.__dict__, index=[0])
                df_union = pd.concat([df_union, df_house])
            df_union.to_excel(str_output_file)
            print(f"Output file: {str_output_file}")
        case 3:
            with open(str_output_file, "w") as file:
                json.dump([house.__dict__ for house in list_houses], file, indent=4)
            print(f"Output file: {str_output_file}")
        case 4:
            str_separator = "-"*40
            for house in list_houses:
                print(f"{str_separator}\n")
                for key, value in house.__dict__.items():
                    print(f"{key}: {value}")
        case _:
            pass


#################
# PROGRAM START #
#################
date_today = datetime.today().date()
list_houses = []
 
str_separator = "-"*40
print(f"{str_separator}\nHTML House Parser - Start\n{str_separator}")

bool_continue = True
while bool_continue:

    # get/validate URL input
    bool_pass_input = False
    while not bool_pass_input:
        var_input = input("Enter CalgaryHomes URL to parse: ")
        bool_pass_input = validators.url(var_input) and "calgaryhomes.ca" in var_input
        if not bool_pass_input:
            print("Invalid input, please enter a valid CalgaryHomes URL!")

    # parse URL page for house info
    print(f"\nParsing house info...")
    house_page = get_html_page(var_input)
    house_parser = HouseParser(var_input)
    house_parser.feed(house_page)
    print(f"House info parsed!")

    house_output = HouseOutput(house_parser.House)
    list_houses.append(house_output)

    """
    str_separator = "-"*20
    print(f"\nEssential Info\n{str_separator}")
    print(house_parser.House.dict_essential_info)
    print(f"\nCommunity Info\n{str_separator}")
    print(house_parser.House.dict_community_info)
    print(f"\nAmenities\n{str_separator}")
    print(house_parser.House.amenities)
    """

    # check if want to continue parsing
    var_input = input("\nContinue? (y/n): ")
    while var_input.lower() not in ["y", "n"]:
        print("Invalid input, please enter y or n")
        var_input = input("\nContinue? (y/n): ")   
    bool_continue = True if var_input.lower() == "y" else False

# get/validate output format option
var_input = input("""
Output format options:
[1] csv 
[2] xlsx (excel)
[3] json
[4] cli (command line)
Enter number for output choice: """
)

while not var_input.isdigit() or int(var_input) not in [1, 2, 3, 4]:
    print("\nInvalid input, please enter a number from 1-4")
    var_input = input("""
Output format options:
[1] csv 
[2] xlsx (excel)
[3] json
[4] cli (command line)
Enter number for output choice: """
    )
int_output_format = int(var_input)

output_house_list(int_output_format, list_houses, date_today)

exit()

