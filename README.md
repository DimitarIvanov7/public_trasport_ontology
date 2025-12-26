# Онтология за градски транспорт

## 1. Въведение

Градският обществен транспорт представлява сложна система от взаимосвързани обекти като спирки, маршрути, превозни средства, пътувания, трансфери и пешеходни връзки. Управлението и анализът на такива системи изисква модел, който да позволява не само съхранение на данни, но и извличане на зависимости и логически изводи.

Целта на проекта е проектиране и реализиране на онтология за градски транспорт, базирана на реални транспортни данни. Онтологията моделира обекти и връзки в домейна и позволява извеждане на нови знания чрез дескриптивни логики и OWL.

---

## 2. Преглед и анализ на съществуващи решения

Използван е стандартът GTFS (General Transit Feed Specification), който описва транспортна информация чрез релационни таблици (CSV файлове). Въпреки широкото си разпространение, GTFS не предлага семантично моделиране и логическо извеждане на знания.

Генерирано от изкуствен интелект решение предложи подобна онтология, но създаде връзки между класове, които не могат да бъдат директно реализирани на базата на предложените таблици.

---

## 3. Използвани данни

Използвано е множество от данни във формат GTFS, включващо следните файлове:

### stops.csv — Спирки
- stop_id  
- stop_name  
- stop_lat  
- stop_lon  
- location_type  
- parent_station  
- level_id  
- wheelchair_boarding  

### routes.csv — Линии
- route_id  
- agency_id  
- route_short_name  
- route_long_name  
- route_type  
- route_color  
- route_text_color  

### trips.csv — Пътувания
- trip_id  
- route_id  
- service_id  
- trip_headsign  
- direction_id  
- wheelchair_accessible  

### stop_times.csv — Времена по спирки
- trip_id  
- arrival_time  
- departure_time  
- stop_id  
- stop_sequence  
- pickup_type  
- drop_off_type  

### transfers.csv — Прекачвания
- from_stop_id  
- to_stop_id  
- from_route_id  
- to_route_id  
- from_trip_id  
- to_trip_id  
- transfer_type  
- min_transfer_time  

### pathways.csv — Пешеходни връзки
- pathway_id  
- from_stop_id  
- to_stop_id  
- pathway_mode  
- is_bidirectional  
- length  
- traversal_time  

### levels.csv — Нива
- level_id  
- level_index  
- level_name  

### fare_attributes.csv — Тарифи
- fare_id  
- price  
- currency_type  
- payment_method  
- transfers  
- transfer_duration  

---

## 4. Описание на онтологията

### Класове

#### Основни класове
- Stop  
- Route  
- Trip  
- Transfer  
- Pathway  

#### Подкласове

**Маршрути:**
- BusRoute  
- TramRoute  
- TrolleyRoute  

**Пътувания:**
- WheelchairFriendlyTrip  

**Трансфери:**
- FastTransfer  
- SlowTransfer  

**Пътеки:**
- ElevatorPathway  
- StairsPathway  
- EscalatorPathway  
- Walkway  

#### Съставни концепти
- AccessibleStop  
- OnlyStairsAccessibleStop  

---

### Свойства

#### Обектни свойства
- hasStop / isStopOf  
- hasTrip / belongsToRoute  
- fromStop  
- toStop  
- connectsTransportElement  
- connectsStop  
- isConnectedBy  
- connectedTo  

#### Данни свойства
- stopName  
- locationType  
- routeType  
- routeShortName  
- tripHeadsign  
- wheelchairAccessible  
- pathwayMode  
- isBidirectional  
- minTransferTime  

---

## 5. Дескриптивни логики

- AND (⊓)  
- EXISTS (∃)  
- hasValue  
- ALL (∀)  
- Cardinality и datatype ограничения  

---

## 6. Използвани технологии

- Python  
- Owlready2  
- Pandas  

---

## 7. Заключение

Онтологията включва 17 концепта, 19 свойства и над 2000 индивида. Реализирани са съставни концепти с EXISTS, ALL и hasValue ограничения. Проектът предоставя основа за бъдещо развитие и анализ на транспортни мрежи.

---

## 8. Използвани източници

- Owlready2 Documentation  
- Google – General Transit Feed Specification (GTFS)  
- Отворени данни за градската мобилност за град София
