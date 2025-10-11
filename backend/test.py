# from intern_bot.data_scraper.scrapers import NokiaScraper
# from intern_bot.data_scraper.scrapers import PWRScraper
# from intern_bot.data_scraper.scrapers import SiiScraper
from intern_bot.data_scraper import DataScraper
from intern_bot.data_manager import DataManager
# DataScraper.scrape_nokia_offers()
# DataScraper.scrape_sii_offers()
# print(DataScraper.scrape_pwr())
# nokia = {'Id': '22192', 'Title': 'Operations Assistant- Working Student (Wroclaw)', 'PostedDate': '2025-06-20', 'PostingEndDate': None, 'Language': 'US', 'PrimaryLocationCountry': 'PL', 'GeographyId': 300000000471967, 'HotJobFlag': False, 'WorkplaceTypeCode': 'ORA_HYBRID', 'JobFamily': None, 'JobFunction': None, 'WorkerType': None, 'ContractType': None, 'ManagerLevel': None, 'JobSchedule': None, 'JobShift': None, 'JobType': None, 'StudyLevel': None, 'DomesticTravelRequired': None, 'InternationalTravelRequired': None, 'WorkDurationYears': None, 'WorkDurationMonths': None, 'WorkHours': None, 'WorkDays': None, 'LegalEmployer': None, 'BusinessUnit': None, 'Department': None, 'Organization': None, 'MediaThumbURL': None, 'ShortDescriptionStr': 'Working Student is a long-term paid internship, that allows you to kickstart your fabulous journey in the IT and Telecom world. As our Trainee you can have experience working in such areas that correspond to full-time engineering jobs. The internship usually lasts from 6 to 24 months. We are open to flexible working hours so that you can reconcile working with us with your studies. #OpenToYou.', 'PrimaryLocation': 'Poland', 'Distance': 1750377600000.0, 'TrendingFlag': False, 'BeFirstToApplyFlag': False, 'Relevancy': 5.956839561462402, 'WorkplaceType': 'Hybrid', 'ExternalQualificationsStr': None, 'ExternalResponsibilitiesStr': None, 'secondaryLocations': [], 'otherWorkLocations': [], 'workLocation': [{'LocationId': 300000011428712, 'LocationName': 'West Link', 'AddressLine1': 'Szybowcowa Street 2', 'AddressLine2': None, 'AddressLine3': None, 'AddressLine4': None, 'Building': None, 'TownOrCity': 'Wroclaw', 'PostalCode': '54-130', 'Country': 'PL', 'Region1': None, 'Region2': None, 'Region3': None, 'Latitude': 51.12619, 'Longitude': 16.97016}], 'requisitionFlexFields': []}
# sii = {'offerId': 34151, 'title': 'Flutter Developer', 'workModes': [{'code': '907000001', 'name': 'Hybrydowa'}, {'code': '907000002', 'name': 'Stacjonarna'}], 'locations': [{'code': 'PL', 'name': 'Polska', 'locations': [{'code': 'PL_CRACOW', 'name': 'Kraków'}]}], 'seniorities': [{'code': 'SENIOR', 'name': 'Senior'}], 'internationalFreelancer': 'no', 'type': 'NORMAL', 'managerialPosition': False}
# pwr = {'title': 'Wsparcie inżyniera jakości', 'company': 'Parker Hannifin Manufacturing Polska', 'location': 'Polska', 'date': '1 lipca 2025', 'link': 'https://biurokarier.pwr.edu.pl/oferty-pracy/wsparcie-inzyniera-jakosci/'}

# print("PWR")
# print(pwr.keys())

# print("nokia")
# print(nokia['ShortDescriptionStr'])


# print("sii")
# print(sii.keys())


# for o in offers:
#     print(50*'=')
#     o


def add_offers():
    links = DataScraper.scrape_offers('Sii')
    offers = DataScraper.scrape_offers_details('Sii', links[:3])
    for o in offers[:20]:
        DataManager.add_offer(o)



def show_all_offers():
    offers = DataManager.get_current_offers()

    if not offers:
        print("Brak ofert w bazie danych.")
        return

    for i, offer in enumerate(offers, 1):
        print(f"\n=== Oferta {i} ===")
        print(f"ID: {offer['id']}")
        print(f"Source: {offer['source']}")
        print(f"Title: {offer['title']}")
        print(f"Company: {offer['company']}")
        print(f"Location: {offer['location']}")
        print(f"Contract Type: {offer['contract_type']}")
        print(f"Date Posted: {offer['date_posted']}")
        print(f"Date Closing: {offer['date_closing']}")
        print(f"Link: {offer['link']}")
        print(f"Description: {offer['description'][:300]}{'...' if len(offer['description']) > 300 else ''}")
        # print(f"embedding {offer['embedding']}")




if __name__ == "__main__":
    # DataManager.create_vector_index()
    # show_all_offers()
    # add_offers()
    show_all_offers()

    # results = DataManager.similarity_search_cosine(
    #     "Poszukujemy Analityka Biznesowo-Systemowego, który dołączy do projektu w sektorze bankowym",
    #     k=3,
    # )
    # for r in results:
    #     print(r)
