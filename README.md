# Stellarium — Ancient Indian Clock (Python, Streamlit, Astropy)

**An interactive, open-source planetarium and ancient Indian timekeeping demo — built with Python, Astropy, Plotly, and Streamlit.**  
Explore the night sky, visualize celestial motions, and discover how ancient Indian astronomers measured time using the sky!

---

## 🌌 What Does This Application Offer?

**Stellarium — Ancient Indian Clock** is a visually rich, educational, and computational tool that:

- **Displays a live, interactive sky dome** (3D or classic 2D view) showing bright stars and their positions from any Earth location.
- **Calculates ancient Indian time units** (Ghaṭi, Muhūrta, Yāma) based on sunrise and sidereal time, in real time.
- **Shows Panchang details** (Tithi, Nakshatra, Yoga, Karana, and Vaar) for the selected date and location.
- **Lets you select stars and compute their meridian transit times**, or solve for the local time from observed alt/az positions.
- **Offers full user control** for observer location, date, time, reference star, sky view mode, and display options.
- **Auto-refreshes in real time**, updating the clock and sky plot every second and every 20 minutes respectively.

**Perfect for students, educators, astronomy enthusiasts, and those curious about ancient Indian timekeeping!**

---

## 🧭 Functional Areas

### 1. Sky Visualization
- **3D Planetarium Dome**: Drag/rotate and zoom to view the simulated sky as seen from your location.
- **2D Altitude-Azimuth Chart**: Traditional sky chart with altitude vs azimuth axes.

### 2. Observer & Clock Panel
- Set your latitude, longitude, altitude, and timezone.
- Pick any date and time.
- See real-time local and sidereal time.

### 3. Ancient Indian Clock Calculations
- **Ghaṭi**: Divides daylight into 60 units.
- **Muhūrta**: 1/30th of a day.
- **Yāma**: 1/8th of a day.
- Calculation begins from local sunrise.

### 4. Panchang Details
- Shows **Tithi**, **Nakshatra**, **Yoga**, **Karana**, **Vaar** for current selection.
- (Demo values, extendable to full astronomical calculations or API integration).

### 5. Star Selection & Solvers
- Pick a star and see its details (RA, Dec, magnitude, Alt/Az).
- Compute meridian transit time (when it crosses the local meridian).
- Solve for time from observed Alt/Az.

---

## 📚 Key Terminologies & Definitions

- **Sidereal Time**: Timekeeping based on Earth's rotation relative to fixed stars, not the Sun.
- **Ghaṭi**: Traditional Indian unit for dividing daylight, 1 ghaṭi ≈ 24 minutes.
- **Muhūrta**: Ancient unit, 1 muhūrta ≈ 48 minutes.
- **Yāma**: 1/8th of a day, a larger ancient unit.
- **Tithi**: Lunar day, determined by the angular separation between Moon and Sun.
- **Nakshatra**: Lunar mansion, one of 27 sectors along the ecliptic.
- **Yoga & Karana**: Other time divisions in Panchang, combining positions of Sun and Moon.
- **Vaar**: Day of the week.
- **Meridian Transit**: Instant when a celestial object crosses the observer’s local meridian (highest point in the sky).

---

## 🧠 Domain-Based Knowledge

### Astronomy & Celestial Mechanics

- **Astropy** powers all coordinate and time transformations, including local sidereal time and positions of Sun and stars.
- **Plotly** enables interactive, visually engaging 3D/2D sky views.

### Ancient Indian Timekeeping

- **Ancient clocks** started the day at sunrise, dividing daylight into Ghaṭi, Muhūrta, Yāma.
- **Panchang**: The Indian almanac, combining solar and lunar positions to define auspicious timings.

### Mathematical Processes

- **Sunrise Calculation**: Uses altitude crossing by the Sun (-0.833°) to estimate sunrise time.
- **Star Position Calculation**: Converts RA/Dec to Alt/Az for the observer’s time and location.
- **Numerical Solvers**: Bisection and ternary search methods to find meridian transits or matching observed positions.

---

## ⏳ Ancient Calculation Process

### Step-By-Step

1. **Observer chooses location, date, and time.**
2. **Sunrise is computed numerically** by finding when the Sun’s altitude crosses -0.833°, accounting for atmospheric refraction.
3. **Ancient time units** (Ghaṭi, Muhūrta, Yāma) are calculated as the time elapsed since sunrise.
4. **Sidereal time** is found for the observer’s longitude, crucial for traditional timekeeping.
5. **Star positions** are updated in real time, allowing for interactive exploration and transit computations.
6. **Panchang elements** are (demo) displayed—these can be calculated using the positions of Sun and Moon.

---

## 🚀 Potential Future Development Areas

- **Full Panchang Calculations**: Integrate algorithms/API for accurate Tithi, Nakshatra, Yoga, Karana based on planetary positions.
- **Deeper Star Catalogs**: Include HYG, Hipparcos, or Gaia catalogs for thousands of stars.
- **Ephemeris Integration**: Add planetary positions, lunar phases, eclipses, and other phenomena.
- **Mobile and Touch UI**: Optimize for smartphones and tablets.
- **Educational Overlays**: Add legends, tooltips, and info panels for students.
- **Multilingual Support**: Offer UI and terminology in major Indian languages.
- **Customizable Almanac Generation**: Allow users to generate and export daily/annual Panchang reports.
- **Advanced Time Solvers**: Implement root-finding for complex astronomical events and ancient calendar conversions.

---

## 💡 Get Involved

**This project is open-source and welcomes contributions!**  
If you’d like to add features, fix bugs, or improve documentation, please open issues or pull requests.

---

## 📝 License

MIT License — Free for use, modification, and distribution.

---

## 👨‍💻 Credits

Built by [helplessThor]  , powered by [Astropy](https://www.astropy.org/), [Plotly](https://plotly.com/), and [Streamlit](https://streamlit.io/).

---

## 📎 Quickstart

1. **Clone the repository**  
   `git clone https://github.com/helplessThor/Stellarium-Indian-Clock.git`
2. **Install dependencies**  
   `pip install -r requirements.txt`
3. **Run the app**  
   `streamlit run app.py`

---


**Explore the cosmos — and the wisdom of ancient Indian astronomy — interactively!**
