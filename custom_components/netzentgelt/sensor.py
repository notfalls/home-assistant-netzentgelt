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
        for q in ["Q1", "Q2", "Q3", "Q4"]:
            q_start = options.get(f"{year}_{q}_start", "01-01")
            q_end = options.get(f"{year}_{q}_end", "03-31")
            if q_start <= current_month_day <= q_end:
                for t in ["Hochtarif", "Normaltarif", "Nebentarif"]:
                    zeiten = options.get(f"{year}_{q}_{t}_zeiten", [])
                    for zeit in zeiten:
                        start, end = zeit.split("-")
                        start_time = time.fromisoformat(start)
                        end_time = time.fromisoformat(end)
                        if start_time < end_time:
                            if start_time <= current_time < end_time:
                                tarif = t
                                break
                        else:
                            if current_time >= start_time or current_time < end_time:
                                tarif = t
                                break
                break

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
