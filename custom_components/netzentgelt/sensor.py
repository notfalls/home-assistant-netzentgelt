from datetime import datetime, time
from homeassistant.helpers.entity import Entity

class NetzentgeltSensor(Entity):
    def __init__(self, hass, config_entry):
        self.hass = hass
        self._entry = config_entry
        self._name = "Netzentgelt"
        self._state = None
        self._attr = {}

    def update(self):
        now = datetime.now()
        year = str(now.year)
        current_month_day = now.strftime("%m-%d")
        current_time = now.time()

        options = self._entry.options

        tarif = "Unbekannt"
        tarif_found = False # Flag to indicate if tarif has been found
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            q_start = options.get(f"{year}_{q}_start", "01-01")
            q_end = options.get(f"{year}_{q}_end", "03-31")
            if q_start <= current_month_day <= q_end:
                for t in ["Hochtarif", "Normaltarif", "Nebentarif"]:
                    zeiten = options.get(f"{year}_{q}_{t}_zeiten", [])
                    for zeit_spanne in zeiten: # Renamed 'zeit' to 'zeit_spanne'
                        start_str, end_str = zeit_spanne.split("-") # Renamed 'start' and 'end'
                        start_time_obj = time.fromisoformat(start_str) # Renamed 'start_time'
                        end_time_obj = time.fromisoformat(end_str) # Renamed 'end_time'
                        if start_time_obj < end_time_obj:
                            if start_time_obj <= current_time < end_time_obj:
                                tarif = t
                                tarif_found = True
                                break # Break from 'zeiten' loop
                        else:  # Handles overnight tariffs
                            if current_time >= start_time_obj or current_time < end_time_obj:
                                tarif = t
                                tarif_found = True
                                break # Break from 'zeiten' loop
                    if tarif_found:
                        break # Break from 't' (tarif types) loop
            if tarif_found:
                break # Break from 'q' (quarters) loop

        preis = float(options.get(f"{year}_{tarif}_preis", 0))
        self._state = preis
        self._attr = {
            "tarif": tarif,
            "jahr": year
        }

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attr
