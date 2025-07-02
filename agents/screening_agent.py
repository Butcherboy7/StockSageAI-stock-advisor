import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
import re

class ScreeningAgent:
    """Agent responsible for scraping stock data from screener.in"""
    
    def __init__(self):
        self.base_url = "https://www.screener.in"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_top_stocks(self, limit: int = 10) -> List[Dict]:
        """
        Scrape top stocks from screener.in based on market cap
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of dictionaries containing stock information
        """
        try:
            # Try to get stocks from the main screener page
            stocks = self._scrape_market_cap_stocks(limit)
            
            if not stocks:
                # Fallback to hardcoded popular stocks if scraping fails
                stocks = self._get_fallback_stocks(limit)
            
            return stocks
            
        except Exception as e:
            print(f"Error in screening agent: {e}")
            return self._get_fallback_stocks(limit)
    
    def _scrape_market_cap_stocks(self, limit: int) -> List[Dict]:
        """Scrape stocks from screener.in market cap page"""
        try:
            # URL for top companies by market cap
            url = f"{self.base_url}/screens/71/top-companies-by-market-cap/"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            stocks = []
            
            # Look for the main table containing stock data
            table = soup.find('table', class_='data-table')
            if not table:
                # Try alternative selectors
                table = soup.find('table')
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows[:limit]:
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 3:
                            # Extract company name and ticker
                            name_cell = cells[0]
                            name_link = name_cell.find('a')
                            
                            if name_link:
                                company_name = name_link.text.strip()
                                href = name_link.get('href', '')
                                
                                # Extract ticker from URL
                                ticker_match = re.search(r'/company/([^/]+)/', href)
                                ticker = ticker_match.group(1) if ticker_match else None
                                
                                if ticker and company_name:
                                    # Extract additional data if available
                                    market_cap = cells[1].text.strip() if len(cells) > 1 else 'N/A'
                                    current_price = cells[2].text.strip() if len(cells) > 2 else 'N/A'
                                    
                                    # Clean the ticker (remove .NS if present for yfinance compatibility)
                                    clean_ticker = ticker.replace('.NS', '')
                                    
                                    stock_data = {
                                        'ticker': clean_ticker,
                                        'name': company_name,
                                        'market_cap': market_cap,
                                        'current_price': current_price,
                                        'source': 'screener.in'
                                    }
                                    
                                    stocks.append(stock_data)
                                    
                    except Exception as e:
                        print(f"Error parsing row: {e}")
                        continue
            
            # Add small delay to be respectful
            time.sleep(random.uniform(1, 2))
            
            return stocks
            
        except Exception as e:
            print(f"Error scraping market cap stocks: {e}")
            return []
    
    def _get_individual_stock_data(self, ticker: str) -> Optional[Dict]:
        """Get detailed data for a specific stock"""
        try:
            url = f"{self.base_url}/company/{ticker}/"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract company name
            name_elem = soup.find('h1')
            company_name = name_elem.text.strip() if name_elem else ticker
            
            # Extract current price
            price_elem = soup.find('span', class_='number')
            current_price = price_elem.text.strip() if price_elem else 'N/A'
            
            # Extract market cap from the ratios section
            market_cap = 'N/A'
            ratios_section = soup.find('section', {'id': 'ratios'})
            if ratios_section:
                for li in ratios_section.find_all('li'):
                    if 'Market Cap' in li.text:
                        market_cap = li.find('span', class_='number').text.strip()
                        break
            
            stock_data = {
                'ticker': ticker,
                'name': company_name,
                'current_price': current_price,
                'market_cap': market_cap,
                'source': 'screener.in'
            }
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 2))
            
            return stock_data
            
        except Exception as e:
            print(f"Error getting data for {ticker}: {e}")
            return None
    
    def _get_fallback_stocks(self, limit: int) -> List[Dict]:
        """Fallback list of popular Indian stocks"""
        popular_stocks = [
            {'ticker': 'RELIANCE', 'name': 'Reliance Industries Limited'},
            {'ticker': 'TCS', 'name': 'Tata Consultancy Services Limited'},
            {'ticker': 'HDFCBANK', 'name': 'HDFC Bank Limited'},
            {'ticker': 'INFY', 'name': 'Infosys Limited'},
            {'ticker': 'ICICIBANK', 'name': 'ICICI Bank Limited'},
            {'ticker': 'HINDUNILVR', 'name': 'Hindustan Unilever Limited'},
            {'ticker': 'ITC', 'name': 'ITC Limited'},
            {'ticker': 'SBIN', 'name': 'State Bank of India'},
            {'ticker': 'BHARTIARTL', 'name': 'Bharti Airtel Limited'},
            {'ticker': 'KOTAKBANK', 'name': 'Kotak Mahindra Bank Limited'},
            {'ticker': 'LT', 'name': 'Larsen & Toubro Limited'},
            {'ticker': 'ASIANPAINT', 'name': 'Asian Paints Limited'},
            {'ticker': 'MARUTI', 'name': 'Maruti Suzuki India Limited'},
            {'ticker': 'HCLTECH', 'name': 'HCL Technologies Limited'},
            {'ticker': 'AXISBANK', 'name': 'Axis Bank Limited'},
            {'ticker': 'TITAN', 'name': 'Titan Company Limited'},
            {'ticker': 'ULTRACEMCO', 'name': 'UltraTech Cement Limited'},
            {'ticker': 'WIPRO', 'name': 'Wipro Limited'},
            {'ticker': 'NESTLEIND', 'name': 'Nestle India Limited'},
            {'ticker': 'POWERGRID', 'name': 'Power Grid Corporation of India Limited'}
        ]
        
        # Return the requested number of stocks
        selected_stocks = popular_stocks[:limit]
        
        # Add additional metadata
        for stock in selected_stocks:
            stock.update({
                'market_cap': 'N/A',
                'current_price': 'N/A',
                'source': 'fallback'
            })
        
        return selected_stocks
    
    def validate_ticker(self, ticker: str) -> bool:
        """Validate if a ticker exists on screener.in"""
        try:
            url = f"{self.base_url}/company/{ticker}/"
            response = self.session.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def search_company(self, query: str) -> List[Dict]:
        """Search for companies on screener.in"""
        try:
            # This would implement the search API that sends requests for each keystroke
            # For now, we'll use a simple approach
            search_url = f"{self.base_url}/api/company/search/?q={query}"
            
            response = self.session.get(search_url, timeout=5)
            
            if response.status_code == 200:
                # Parse search results (implementation depends on API response format)
                return response.json()
            else:
                return []
                
        except Exception as e:
            print(f"Search error: {e}")
            return []
