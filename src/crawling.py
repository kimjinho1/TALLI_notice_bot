from Saramin import Saramin

# crawling & save saramin job posting data
if __name__ == "__main__":
    saramin_crawler = Saramin("today")
    # saramin_crawler = Saramin("all")
    saramin_crawler.crawling()
