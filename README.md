# Tamil Calendar Source Code

### தமிழ் காலண்டர் கணக்கீட்டு நிரல்

An open-source Tamil Calendar calculation engine that determines Tamil months, dates, and year cycles using astronomical solar transit calculations.

சூரியன் ராசி மாற்றம், லஹிரி அயனாம்சம் மற்றும் பாரம்பரிய 13 கடிகை விதியை பயன்படுத்தி தமிழ் மாதங்கள், தேதிகள் மற்றும் வருட சுழற்சிகளை கணக்கிடும் திறந்த மூல நிரல்.

---

# Overview

### அறிமுகம்

The Tamil Calendar is a **solar-sidereal calendar** based on the movement of the Sun through the 12 zodiac signs.

Each Tamil month begins when the Sun enters a new **Rasi (zodiac sign)**.

தமிழ் காலண்டர் என்பது **சூரிய-நட்சத்திர காலண்டர்** ஆகும்.
சூரியன் 12 ராசிகளுக்குள் நகர்வதை அடிப்படையாகக் கொண்டு மாதங்கள் கணக்கிடப்படுகின்றன.

சூரியன் ஒரு புதிய ராசிக்குள் நுழையும் நேரத்தில் அந்த தமிழ் மாதம் தொடங்குகிறது.

---

# Key Features

### முக்கிய அம்சங்கள்

**English**

* Tamil month calculation from solar transit
* Tamil year (60-year cycle)
* Lahiri Ayanamsa sidereal calculations
* Sunrise-based calendar logic
* Traditional **13-Ghatika rule** implementation
* Precise astronomical calculations using Swiss Ephemeris

**தமிழ்**

* சூரிய பெயர்ச்சியை அடிப்படையாகக் கொண்டு தமிழ் மாத கணக்கீடு
* 60 வருட தமிழ் வருட சுழற்சி
* லஹிரி அயனாம்சம் பயன்படுத்திய நட்சத்திர கணக்கீடு
* சூரிய உதய அடிப்படையிலான நாள் தீர்மானம்
* பாரம்பரிய **13 கடிகை விதி** செயல்படுத்தல்
* Swiss Ephemeris மூலம் துல்லியமான கோளரிதல் கணக்கீடு

---

# How the Calendar is Calculated

### காலண்டர் எப்படி கணக்கிடப்படுகிறது

### 1. Solar Longitude

The position of the Sun is calculated using astronomical ephemeris data.

### 2. Sidereal Conversion

Sidereal longitude is obtained using Lahiri Ayanamsa.

**Formula**

Sidereal Longitude = Tropical Longitude − Ayanamsa

### 3. Tamil Month Determination

Each zodiac sign corresponds to a Tamil month.

| Rasi      | Tamil Month |
| --------- | ----------- |
| Mesha     | Chithirai   |
| Rishabha  | Vaikasi     |
| Mithuna   | Aani        |
| Kataka    | Aadi        |
| Simha     | Avani       |
| Kanya     | Purattasi   |
| Tula      | Aippasi     |
| Vrischika | Karthigai   |
| Dhanus    | Margazhi    |
| Makara    | Thai        |
| Kumbha    | Maasi       |
| Meena     | Panguni     |

---

# 13-Ghatika Rule

### 13 கடிகை விதி

A traditional rule used to determine the **first day of a Tamil month**.

1 Ghatika = 24 minutes
13 Ghatikas = 312 minutes (5 hours 12 minutes)

Rule:

If solar transit occurs within **312 minutes after sunrise**,
that day becomes the **first day of the Tamil month**.

Otherwise, the **next day becomes the first day**.

தமிழ் மாதத்தின் முதல் நாளை தீர்மானிக்க பயன்படும் பாரம்பரிய விதி.

சூரிய பெயர்ச்சி சூரிய உதயத்திற்கு பிறகு **312 நிமிடங்களுக்குள்** நடந்தால்
அந்த நாளே தமிழ் மாதத்தின் முதல் நாள்.

312 நிமிடங்களுக்கு பிறகு நடந்தால்
**அடுத்த நாள்** மாதத்தின் முதல் நாள் ஆகும்.

---

# Project Structure

### திட்ட அமைப்பு

```
tamil-calendar/
│
├── tamil_calendar.py   # core astronomy calculations
├── app.py              # Flask API server
└── index.html          # frontend calendar interface
```

---

# Requirements

### தேவையானவை

* Python 3.10+
* pyswisseph
* flask

Install dependencies:

```
pip install pyswisseph flask
```

---

# Running the Application

### நிரலை இயக்குவது

Run the Flask server:

```
python app.py
```

Open your browser:

```
http://localhost:5050
```

---

# License

### உரிமம்

This project is released under the **MIT License**.

இந்த திட்டம் **MIT License** கீழ் வெளியிடப்பட்டுள்ளது.

---

