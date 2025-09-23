# In the name of the Machine God,
# this scripture defines the protocol for the Adeptus Mechanicus.
# Its purpose is to scout the chaotic seas of the market
# and identify signals worthy of the Omnissiah's blessing.

import json
import logging
from time import sleep
from bybit_tools import get_top_volume_symbols, servitor_fetch_market_data
from data_processor import tech_priest_analyze_data
from archmagos import archmagos_forge_signal

# Configure logging to record the machine spirit's thoughts
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_adeptus_mechanicus_cycle(symbols_to_scout: list):
    """
    The main operational loop that orchestrates all units of the Adeptus
    Mechanicus.
    """
    logging.info("=== ADEPTUS MECHANICUS SCOUTING CYCLE INITIATED ===")

    for symbol in symbols_to_scout:
        # 1. Servitor fetches data
        market_data_df = servitor_fetch_market_data(symbol, 5, 200)

        if market_data_df is None or market_data_df.empty:
            logging.warning(f"Could not proceed for {symbol}, data was not retrieved.")
            continue  # Move to the next symbol

        # 2. Tech-Priest analyzes data
        enriched_df, analysis_dict = tech_priest_analyze_data(market_data_df)

        # 3. Archmagos forges the signal
        primaris_signal = archmagos_forge_signal(enriched_df, analysis_dict, symbol)

        if primaris_signal:
            logging.info("Signal has been forged and is ready for the next stage.")
            # In a full system, you would now send this signal to the Magos
            # Strategos or Astra Militarum
            print("\n--- PRIMARIS SIGNAL FORGED ---")
            print(json.dumps(primaris_signal, indent=2))
            print("----------------------------\n")
        
        sleep(3)
        logging.info("=== MOVING ON TO NEXT COIN. ===")

    logging.info("=== SCOUTING CYCLE COMPLETE. AWAITING NEXT DIRECTIVE. ===")

if __name__ == "__main__":
    # 1. Servitor scouts for the top 50 symbols by volume
    scouting_list = get_top_volume_symbols(limit=50)
    print(f"Scouting List: {scouting_list}")
    
    if scouting_list:
        # 2. Run the main cycle with the scouted symbols
        run_adeptus_mechanicus_cycle(scouting_list)

    else:
        logging.error("Could not retrieve scouting list. Terminating directive.")