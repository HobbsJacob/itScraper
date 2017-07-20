#output.csv stores listings
#listingNumbers.csv stores the id of currently stored listings so they are not duplicated
#duplicates data but is faster than searching through output.csv

from bs4 import BeautifulSoup
import requests
import re

class Listing:                          #Listing class, will be more usefull when analysing the scraped data
    def __init__(self, number):
        self.title = ""
        self.number = number
        self.category = ""
        self.listed = ""
        self.jType = ""
        self.location = ""
        self.pay = ""
        self.description = ""

    def csv_row(self):                                                                  #Could also use the built in CSV writer, but this is easier
        self.title = self.title.replace(";", ";").strip("\n")
        self.number = self.number.replace(";", ";").strip("\n")
        self.category = self.category.replace(";", ";").strip("\n")
        self.listed = self.listed.replace(";", ";").strip("\n")
        self.jType = self.jType.replace(";", ";").strip("\n")
        self.location = self.location.replace(";", ";").strip("\n")
        self.pay = self.pay.replace(";", ";").strip("\n")
        self.description = self.description.replace(";", ";").strip("\n")
        
        return(self.title + ";" + self.number + ";" +  self.category + ";" + self.listed + ";" +
               self.jType + ";" + self.location + ";" + self.pay + ";" + self.description + "\n")


previousListings = []

with open("listingNumbers.csv", "r") as numbersFile:        #Read the numbers of all listings currently stored
    for line in numbersFile:
        previousListings.append(line.strip("\n"))

baseUrl = "http://www.trademe.co.nz"

page = requests.get("http://www.trademe.co.nz/Browse/CategoryAttributeSearchResults.aspx?sort_order=167_desc&search=1&cid=5000&sidebar=1&selected141=&140=&154=5112&155=&153=&142=FT&jobsPayType=on%2CSALARY&144=-1%2C2147483647&sidebarSearch_keypresses=0&sidebarSearch_suggested=0")

soup = BeautifulSoup(page.content, "html.parser")


listingUrls = []

print("Getting listing URLs")
while True:
    for tag in soup.find_all("a", id=re.compile("JobCardTitleLink")):       #Find each listing link
        listingUrls.append(tag.get("href"))
        
    nextPage = soup.find("a", rel="next")                                   #Find the "Next" link to move to the next page

    if(nextPage == None):
        break
    else:
        url = baseUrl + nextPage.get("href")
        soup = BeautifulSoup(requests.get(url).content, "html.parser")
    
print("Getting listing details")

listings = []

for listing in listingUrls:
    page = requests.get(baseUrl + listing)
    soup = BeautifulSoup(page.content, "html.parser")

    currentListing = Listing(re.sub("\D", "", listing))     #Create new listing with it's ID from URL
    
    if currentListing.number not in previousListings:
        currentListing.title = soup.find("header").text         #Add title

        splitUrl = listing.split("/")                           #Job category is after '/it/' in the url
        currentListing.category = splitUrl[splitUrl.index("it") + 1]
        
        attributes = soup.find("div", class_="j-attributes")    #Find attributes DIV
        for tag in attributes.find_all("tr"):
            data = tag.find_all("td")
            if ("Listed" in data[0].text):
                currentListing.listed = data[1].text
            elif ("Type" in data[0].text):
                currentListing.type = data[1].text
            elif ("Location" in data[0].text):
                currentListing.location = data[1].text
            elif ("Pay & Benefits" in data[0].text):
                currentListing.pay = data[1].text
        
        currentListing.description = soup.find("div", class_="j-description").text  #Add description
        
        listings.append(currentListing)
    
print("Writing to CSV")

with open("output.csv", "a") as outFile:
    with open("listingNumbers.csv", "a") as numberFile:     #Write entire listing to output.csv and id to listingNumbers.csv
        for listing in listings:
            outFile.write(listing.csv_row())
            numberFile.write(listing.number + "\n")


print("Done")
    
