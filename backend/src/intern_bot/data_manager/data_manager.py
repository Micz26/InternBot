from typing import Any
from datetime import date

import psycopg2
from psycopg2.extras import execute_values
from langchain_openai import OpenAIEmbeddings

from intern_bot.settings import Settings


class DataManager:
    settings = Settings()
    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY.get_secret_value())

    @staticmethod
    def _get_connection():
        return psycopg2.connect(
            host=DataManager.settings.DB_HOST,
            port=DataManager.settings.DB_PORT,
            dbname=DataManager.settings.DB_NAME,
            user=DataManager.settings.DB_USER,
            password=DataManager.settings.DB_PASSWORD.get_secret_value()
        )
    
    @staticmethod
    def create_vector_index():
        """
        Creates an IVF index on the embedding column using cosine similarity.
        This should be run once after the table and embeddings are populated.
        """
        try:
            with DataManager._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        CREATE INDEX IF NOT EXISTS offers_embedding_ivfflat_idx
                        ON {DataManager.settings.OFFERS_TABLE_NAME}
                        USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100);
                    """)
                    cur.execute(f"ANALYZE {DataManager.settings.OFFERS_TABLE_NAME};")
                    conn.commit()
            print("Vector index created successfully.")
        except Exception as e:
            print(f"Error creating vector index: {e}")

    
    @staticmethod
    def get_current_offers() -> list[dict[str, str]]:
        try:
            with DataManager._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT id, source, link, title, company, location, contract_type, date_posted, date_closing, description, embedding FROM {DataManager.settings.OFFERS_TABLE_NAME}")
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error fetching all offers: {e}")
            return []
        
    @staticmethod
    def get_offer(id: str) -> dict[str, str] | None:
        try:
            with DataManager._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        SELECT id, source, link, title, company, location, contract_type, date_posted, date_closing, description
                        FROM {DataManager.settings.OFFERS_TABLE_NAME}
                        WHERE id = %s
                    """, (id))
                    row = cur.fetchone()
                    if row:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, row))
                    return None
        except Exception as e:
            print(f"Error fetching offer {id} : {e}")
            return None

    @staticmethod
    def add_offer(offer: dict[str, str]):
        try:
            description = offer.get("description", "")
            embedding = DataManager.embeddings.embed_query(description)

            conn = DataManager._get_connection()

            cur = conn.cursor()

            query = f"""
                INSERT INTO {DataManager.settings.OFFERS_TABLE_NAME} (
                    link, title, company, location,
                    contract_type, date_posted, date_closing,
                    source, description, embedding
                )
                VALUES %s
            """

            values = [(
                offer.get("link"),
                offer.get("title"),
                offer.get("company"),
                offer.get("location"),
                offer.get("contract_type"),
                offer.get("date_posted"),
                offer.get("date_closing"),
                offer.get("source"),
                description,
                embedding
            )]

            execute_values(cur, query, values)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Error adding offer {offer['link']}: {e}")

    @staticmethod
    def add_offers(offers: list[dict[str, str]]):
        for offer in offers:
            DataManager.add_offer(offer)


    @staticmethod
    def remove_offer(offer_link: str):
        try:
            with DataManager._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"DELETE FROM {DataManager.settings.OFFERS_TABLE_NAME} WHERE link = %s",
                        (offer_link)
                    )
                    conn.commit()
        except Exception as e:
            print(f"Error removing offer {offer_link}: {e}")

    @staticmethod
    def remove_offers(offers_links: list[int]):
        for link in offers_links:
            DataManager.remove_offer(link)

    @staticmethod
    def get_current_offers_links(source: str | None = None) -> list[dict[str, str]]:
        """Pobiera aktualne oferty z bazy danych (id + source)."""
        try:
            with DataManager._get_connection() as conn:
                if source is not None:
                    with conn.cursor() as cur:
                        cur.execute(f"SELECT link FROM {DataManager.settings.OFFERS_TABLE_NAME} WHERE source = %s", (source,))
                        rows = cur.fetchall()
                        return rows
                else:
                    with conn.cursor() as cur:
                        cur.execute(f"SELECT link FROM {DataManager.settings.OFFERS_TABLE_NAME}")
                        rows = cur.fetchall()
                        return rows                    
        except Exception as e:
            print(f"Error fetching current offers: {e}")
            return []

    @staticmethod
    def diff_offers(
        current_offers: list[str],
        new_offers: list[str]
    ) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
        """
        Zwraca tuple:
        - [nowe oferty] — które są w new_offers, ale nie ma ich w current_offers
        - [usunięte oferty] — które są w current_offers, ale nie ma ich w new_offers
        """
        to_add = set(new_offers) - set(current_offers)
        to_remove = set(current_offers) - set(new_offers)

        return list(to_add), list(to_remove)

    
    @staticmethod
    def get_outdated_offers() -> list[dict[str, str]]:
        """Zwraca oferty, których data zamknięcia już minęła (date_closing < dzisiaj)."""
        try:
            with DataManager._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        SELECT link
                        FROM {DataManager.settings.OFFERS_TABLE_NAME}
                        WHERE date_closing IS NOT NULL AND date_closing < %s
                    """, (date.today(),))
                    rows = cur.fetchall()
                    return rows
        except Exception as e:
            print(f"Error fetching outdated offers: {e}")
            return []
        
    @staticmethod
    def similarity_search_cosine(
        query: str,
        k: int = 5,
        filters: dict[str, Any] | None = None
    ) -> list[dict]:
        """
        Perform similarity search using cosine similarity on the embedding column,
        with optional metadata filters.

        Args:
            query: tekst zapytania do osadzenia i wyszukania.
            k: liczba zwracanych wyników.
            filters: słownik filtrów na metadane, np.
                {
                    "company": "Acme Corp",
                    "location": "Kraków",
                    "contract_type": "full-time",
                    "date_posted_from": "2023-01-01",
                    "date_posted_to": "2023-12-31",
                    "source": "jobboard"
                }

        Returns:
            Lista słowników z wynikami i odległością.
        """
        try:
            query_embedding = DataManager.embeddings.embed_query(query)

            # Budujemy dynamicznie warunki WHERE
            where_clauses = []
            params = [query_embedding]  # pierwszy parametr to embedding

            if filters:
                # Proste filtry równościowe
                for key in ["company", "location", "contract_type", "source"]:
                    if key in filters and filters[key] is not None:
                        where_clauses.append(f"{key} = %s")
                        params.append(filters[key])

                # Filtry zakresowe dla dat
                if "date_posted_from" in filters and filters["date_posted_from"] is not None:
                    where_clauses.append("date_posted >= %s")
                    params.append(filters["date_posted_from"])
                if "date_posted_to" in filters and filters["date_posted_to"] is not None:
                    where_clauses.append("date_posted <= %s")
                    params.append(filters["date_posted_to"])
                if "date_closing_from" in filters and filters["date_closing_from"] is not None:
                    where_clauses.append("date_closing >= %s")
                    params.append(filters["date_closing_from"])
                if "date_closing_to" in filters and filters["date_closing_to"] is not None:
                    where_clauses.append("date_closing <= %s")
                    params.append(filters["date_closing_to"])

            where_sql = ""
            if where_clauses:
                where_sql = "WHERE " + " AND ".join(where_clauses)

            sql = f"""
                SELECT id, link, title, company, location, contract_type, date_posted, date_closing, source, description,
                       embedding <=> %s::vector AS distance
                FROM {DataManager.settings.OFFERS_TABLE_NAME}
                {where_sql}
                ORDER BY distance
                LIMIT %s
            """
            params.append(k)

            with DataManager._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql, params)
                    rows = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            print(f"Error during similarity search: {e}")
            return []