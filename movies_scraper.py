import requests
from bs4 import BeautifulSoup


url_list = {}
api_key = "ff4794c5d342b6e9468eaef55dbe0f0faad12ab0"


def search_movies(query):
    movies_list = []
    website = None
    
    try:
        website = BeautifulSoup(requests.get(f"https://185.53.88.104/?s={query.replace(' ', '+')}", timeout=10).text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching the website: {e}")
        return movies_list
    
    movies = website.find_all("a", {'class': 'ml-mask jt'})
    for movie in movies:
        movies_details = {}  # Create a new dictionary for each movie
        if movie:
            movies_details["id"] = f"link{movies.index(movie)}"
            movies_details["title"] = movie.find("span", {'class': 'mli-info'}).text
            url_list[movies_details["id"]] = movie['href']
            movies_list.append(movies_details)
    
    return movies_list


def get_movie(query):
    movie_details = {}
    movie_page_link = None
    
    # Handle the case where URL may not exist or other issues
    if query not in url_list:
        return movie_details
    
    try:
        movie_page_link = BeautifulSoup(requests.get(f"{url_list[query]}", timeout=10).text, "html.parser")
    except requests.RequestException as e:
        print(f"Error fetching the movie page: {e}")
        return movie_details
    
    if movie_page_link:
        # Safely get movie title
        title_tag = movie_page_link.find("div", {'class': 'mvic-desc'})
        if title_tag and title_tag.h3:
            movie_details["title"] = title_tag.h3.text
        
        # Safely get image URL
        img_tag = movie_page_link.find("div", {'class': 'mvic-thumb'})
        if img_tag and 'data-bg' in img_tag.attrs:
            movie_details["img"] = img_tag['data-bg']
        
        # Process download links
        links = movie_page_link.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
        final_links = {}
        for i in links:
            url = f"https://urlshortx.com/api?api={api_key}&url={i['href']}"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  # Ensure we get a valid response
                link = response.json()
                if 'shortenedUrl' in link:
                    final_links[i.text] = link['shortenedUrl']
            except requests.RequestException as e:
                print(f"Error shortening URL for {i.text}: {e}")
            except ValueError:
                print(f"Error parsing JSON response for {i.text}")
        
        if final_links:
            movie_details["links"] = final_links
    
    return movie_details
