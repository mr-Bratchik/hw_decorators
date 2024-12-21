from datetime import datetime
import requests
from bs4 import BeautifulSoup

def logger(path):
    def __logger(old_function):
        def new_function(*args, **kwargs):
            log = ""
            try:
                result = old_function(*args, **kwargs)
                log = f"[{datetime.now()}] Function: {old_function.__name__}\n"
                if isinstance(result, list):
                    log += (
                        f"Found {len(result)} articles:\n"
                        + "\n".join(result[:5])  # Только первые 5 статей
                        + "\n\n"
                    )
                else:
                    log += f"Result: {result}\n\n"
            except Exception as e:
                log = (
                    f"[{datetime.now()}] Function: {old_function.__name__}\n"
                    f"Error: {e}\n\n"
                )
                raise
            finally:
                if log:  # Лог записывается только если он содержит данные
                    with open(path, "a", encoding="utf-8") as f:
                        f.write(log)

            return result

        return new_function

    return __logger

@logger(path="logs.log")
def main():
    # Ключевые слова для поиска
    keywords = ["дизайн", "фото", "web", "python", "linux", "windows", "mac"]

    # url страницы со статьями
    url = "https://habr.com/ru/articles/"

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        articles = soup.select("article.tm-articles-list__item")

        filtered_articles = []

        for article in articles:
            # Извлечение заголовка
            title_element = article.select_one("h2.tm-title.tm-title_h2")
            title = title_element.text.strip() if title_element else None

            # Извлечение превью-текста
            preview_element = article.select_one("div")
            preview_text = preview_element.text.strip() if preview_element else None

            # Извлечение даты публикации
            date_element = article.select_one("time")
            date = date_element["datetime"] if date_element else None

            # Извлечение ссылки
            link_element = title_element.select_one("a") if title_element else None
            link = f"https://habr.com{link_element['href']}" if link_element else None

            if not title or not link:
                continue

            content = f"{title} {preview_text}".lower()

            if any(keyword.lower() in content for keyword in keywords):
                filtered_articles.append(f"{date} – {title} – {link}")

        for article in filtered_articles:
            print(article)

        return filtered_articles

    except requests.RequestException as e:
        error_message = f"Ошибка при выполнении запроса: {e}"
        print(error_message)
        return error_message
    except Exception as e:
        error_message = f"Произошла ошибка: {e}"
        print(error_message)
        return error_message

if __name__ == "__main__":
    main()
