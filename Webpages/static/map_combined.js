//----------------------- Initialise map -----------------------
const map = L.map('map', {
    center: [-26.2744, 128.7751], // Centered on Australia
    zoom: 5,
    timeDimension: true,
    timeDimensionControl: true,
    timeDimensionOptions: {
        timeInterval: "2000-01-01/2024-07-31",
        autoPlay: false,
        loopButton: true,
        timeSteps: 1,
        timeIntervals: 'P1D',
        currentTime: new Date('2017-01-30T00:00:00Z').getTime(),
        playerOptions: {
            buffer: 1,
            transitionTime: 100,
        }
    }
});

// Add base map layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Restrict the bounds of the map to Australia
const southWest = L.latLng(-55.0, 90.0);
const northEast = L.latLng(-5.0, 180.0);
const australiaBounds = L.latLngBounds(southWest, northEast);
map.setMaxBounds(australiaBounds);
map.setMinZoom(4);

// Helper function to clear existing layers before adding new ones
function clearMapLayers() {
    map.eachLayer((layer) => {
        if (layer instanceof L.Circle) {
            map.removeLayer(layer);
        }
    });
}

// Function to get weather data for a specific date
async function getRainfallData(date) {
    const response = await fetch(`http://127.0.0.1:5000/get_rainfall_data?date=${date}`);
    const data = await response.json();
    console.log("Fetched rain data:", data); // Debugging
    return data;
}

// Function to get temperature data for a specific date
async function getTemperatureData(date) {
    const response = await fetch(`http://127.0.0.1:5000/get_temperature_data?date=${date}`);
    const data = await response.json();
    console.log("Fetched temperature data:", data); // Debugging
    return data;
}

// Color functions for rainfall and temperature
function getRainfallColor(rainsum) {
    return rainsum > 50 ? '#0c2c84' :
        rainsum > 25 ? '#225ea8' :
            rainsum > 15 ? '#41b6c4' :
                rainsum > 5 ? '#7fcdbb' :
                    rainsum > 1 ? '#c7e9b4' :
                        rainsum > 0.5 ? '#edf8b1' :
                            rainsum > 0 ? '#ffffd9' :
                                '#f7fcf0';  // Default for very low/zero rainfall
}

function getTemperatureColor(temperaturemean) {
    return temperaturemean > 40 ? '#67001f' :
        temperaturemean > 35 ? '#b2182b' :
            temperaturemean > 30 ? '#d6604d' :
                temperaturemean > 25 ? '#f4a582' :
                    temperaturemean > 20 ? '#fddbc7' :
                        temperaturemean > 15 ? '#d1e5f0' :
                            temperaturemean > 10 ? '#92c5de' :
                                temperaturemean > 0 ? '#4393c3' :
                                    '#2166ac';
}

// Function to style the temperature choropleth layer
function styleTemperature(feature) {
    return {
        fillColor: getTemperatureColor(feature.properties.temperaturemean),  // Use temperaturemean
        weight: 2,
        opacity: 1,
        color: 'white',  // Border color
        dashArray: '3',
        fillOpacity: 0.7
    };
}

// Function to style the rainfall choropleth layer
function styleRainfall(feature) {
    return {
        fillColor: getRainfallColor(feature.properties.rainsum),  // Use temperaturemean
        weight: 2,
        opacity: 1,
        color: 'white',  // Border color
        dashArray: '3',
        fillOpacity: 0.7
    };
}

// Function to update the map with temperature data
async function updateTemperatureLayer(time) {
    const date = new Date(time).toISOString().split('T')[0]; // Convert time to YYYY-MM-DD format
    const tempData = await getTemperatureData(date);

    clearMapLayers();

    console.log("Total suburbs received:", tempData.features.length);
    console.log("Temperature GeoJSON Data:", tempData); // debug

    // Clear any existing temperature layers before adding new ones
    if (map.temperatureLayer) {
        map.removeLayer(map.temperatureLayer);
    }

    // Define hover styles
    const hoverStyle = {
        weight: 2,
        color: 'yellow',  // Change border color to yellow
        fillColor: 'yellow',  // Change fill color to yellow
        fillOpacity: 0.7
    };

    // Add temperature layer as a GeoJSON choropleth
    map.temperatureLayer = L.geoJSON(tempData, {
        renderer: L.canvas(),
        style: styleTemperature,  // Apply styles
        onEachFeature: function (feature, layer) {
            // Bind a tooltip to show suburb name and temperaturemean
            const suburbName = feature.properties.officialnamesuburb || 'Unknown Suburb';
            const temperatureMean = feature.properties.temperaturemean !== null
                ? feature.properties.temperaturemean + '°C'
                : 'No Data';
            const tooltipContent = `<b>${suburbName}</b><br>Temperature: ${temperatureMean}`;

            layer.bindTooltip(tooltipContent, { sticky: true });

            // Event listener to change color on hover
            layer.on('mouseover', function (e) {
                layer.setStyle(hoverStyle);  // Apply hover style
            });

            // Event listener to reset the color when mouse leaves
            layer.on('mouseout', function (e) {
                map.temperatureLayer.resetStyle(layer);  // Reset to original style
            });
        }
    }).addTo(map);
}

// Function to update the map with rainfall data
async function updateRainfallLayer(time) {
    const date = new Date(time).toISOString().split('T')[0]; // Convert time to YYYY-MM-DD format
    const rainData = await getRainfallData(date);

    clearMapLayers();

    console.log("Total suburbs received:", rainData.features.length);
    console.log("Temperature GeoJSON Data:", rainData); // Debugging

    // Clear any existing temperature layers before adding new ones
    if (map.rainfallLayer) {
        map.removeLayer(map.rainfallLayer);
    }

    // Define hover styles
    const hoverStyle = {
        weight: 2,
        color: 'yellow',  // Change border color to yellow
        fillColor: 'yellow',  // Change fill color to yellow
        fillOpacity: 0.7
    };

    // Add temperature layer as a GeoJSON choropleth
    map.rainfallLayer = L.geoJSON(rainData, {
        renderer: L.canvas(),
        style: styleRainfall,  // Apply styles
        onEachFeature: function (feature, layer) {
            // Bind a tooltip to show suburb name and temperaturemean
            const suburbName = feature.properties.officialnamesuburb || 'Unknown Suburb';
            const rainsum = feature.properties.rainsum !== null
                ? feature.properties.rainsum + 'mm'
                : 'No Data';
            const tooltipContent = `<b>${suburbName}</b><br>Rainfall: ${rainsum}`;

            layer.bindTooltip(tooltipContent, { sticky: true });

            // Event listener to change color on hover
            layer.on('mouseover', function (e) {
                layer.setStyle(hoverStyle);  // Apply hover style
            });

            // Event listener to reset the color when mouse leaves
            layer.on('mouseout', function (e) {
                map.rainfallLayer.resetStyle(layer);  // Reset to original style
            });
        }
    }).addTo(map);
}


// Legends for both layers
const rainfallLegend = L.control({ position: 'bottomright' });
rainfallLegend.onAdd = function (map) {
    const div = L.DomUtil.create('div', 'info legend'),
        grades = [0, 0.5, 1, 5, 15, 25, 50],  // Rainfall thresholds
        colors = ['#ffffd9', '#edf8b1', '#c7e9b4', '#7fcdbb', '#41b6c4', '#225ea8', '#0c2c84'];

    div.innerHTML = '<h4>Rainfall (mm)</h4>';
    for (let i = 0; i < grades.length; i++) {
        div.innerHTML +=
            '<i style="background:' + colors[i] + '"></i> ' +
            grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + '<br>' : '+');
    }
    return div;
};

const temperatureLegend = L.control({ position: 'bottomright' });
temperatureLegend.onAdd = function (map) {
    const div = L.DomUtil.create('div', 'info legend'),
        grades = [-10, 0, 10, 15, 20, 25, 30, 35, 40],
        colors = ['#2166ac', '#4393c3', '#92c5de', '#d1e5f0', '#fddbc7', '#f4a582', '#d6604d', '#b2182b', '#67001f'];

    div.innerHTML = '<h4>Temperature (°C)</h4>';
    for (let i = 0; i < grades.length; i++) {
        const from = grades[i];
        const to = grades[i + 1];
        div.innerHTML +=
            '<i style="background:' + colors[i] + '"></i> ' +
            from + (to ? '&ndash;' + to : ' <') + '<br>';
    }
    return div;
};

// Toggling layers and legends
let currentLayerType = null;
let currentLegend = null;

function toggleLayer(layerType) {
    // Remove the previous layer 
    if (currentLayerType === 'rainfall' && map.rainfallLayer) {
        map.removeLayer(map.rainfallLayer);
    } else if (currentLayerType === 'temperature' && map.temperatureLayer) {
        map.removeLayer(map.temperatureLayer);
    }

    // Remove the previous legend 
    if (currentLegend) {
        map.removeControl(currentLegend);
    }

    // Update to selected layer
    if (layerType === 'rainfall') {
        currentLayerType = 'rainfall';
        updateRainfallLayer(map.timeDimension.getCurrentTime());
        currentLegend = rainfallLegend;
    } else if (layerType === 'temperature') {
        currentLayerType = 'temperature';
        updateTemperatureLayer(map.timeDimension.getCurrentTime());
        currentLegend = temperatureLegend;
    }

    // Update to selected legend
    if (currentLegend) {
        currentLegend.addTo(map);
    }
}

// Initial map load for the temperature layer
toggleLayer('temperature');

// Buttons for toggling between rainfall and temperature
const toggleButtons = L.control({ position: 'bottomleft' });
toggleButtons.onAdd = function () {
    const div = L.DomUtil.create('div', 'toggle-buttons');
    div.innerHTML = `
        <button onclick="toggleLayer('temperature')">Temperature</button>
        <button onclick="toggleLayer('rainfall')">Rainfall</button>
    `;
    return div;
};
toggleButtons.addTo(map);

// Listen for time slider changes
map.timeDimension.on('timeload', function (e) {
    const timestamp = e.time;
    console.log("Time changed:", timestamp);

    if (currentLayerType === 'rainfall') {
        updateRainfallLayer(timestamp);
    } else if (currentLayerType === 'temperature') {
        updateTemperatureLayer(timestamp);
    }
});


// Initialise markers layer and list of suburbs
let markersLayer = L.layerGroup().addTo(map);
let addedSuburbs = [];
let addedSuburbNames = [];

// Autocomplete for suburb input
document.getElementById("suburbs").addEventListener("input", function () {
    const query = this.value;

    if (query.length >= 2) {
        fetch(`http://127.0.0.1:5000/autocomplete?q=${query}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok: ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                const suburbList = document.getElementById("suburb-list");
                suburbList.innerHTML = '';

                data.forEach(suburb => {
                    const option = document.createElement('option');
                    option.value = suburb;
                    suburbList.appendChild(option);
                });
            })
            .catch(error => {
                console.error('Error fetching autocomplete suggestions:', error);
            });
    }
});

// Blurring the input to hide the autocomplete box once an option is selected
document.getElementById("suburbs").addEventListener("change", function () {
    // Once the user selects an option, blur the input to close the autocomplete suggestions
    this.blur();
});

// Handle selection from autocomplete and form submission
document.getElementById("suburbForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const suburbInput = document.getElementById("suburbs").value.trim();

    if (suburbInput && !addedSuburbNames.includes(suburbInput)) {
        addSuburbToMapAndList(suburbInput);
    } else if (addedSuburbNames.includes(suburbInput)) {
        alert(`${suburbInput} is already added to the list.`);
    }

    // Clear the input box after adding the suburb
    document.getElementById("suburbs").value = '';
});

// Function to add suburb to map and list
function addSuburbToMapAndList(suburbName) {
    fetch('http://127.0.0.1:5000/get_suburb_coordinates', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ suburbs: [suburbName] })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            const coordinates = data.coordinates;

            if (coordinates.length === 0) {
                console.error(`No coordinates found for suburb: ${suburbName}`);
                return;
            }

            // Add the marker to the map and the list in a single step
            coordinates.forEach(coordinate => {
                const marker = L.marker([coordinate.latitude, coordinate.longitude])
                    .bindPopup(`<b>${coordinate.suburb}</b>`)
                    .addTo(markersLayer);

                addedSuburbs.push({ suburb: coordinate.suburb, marker: marker });
                addedSuburbNames.push(coordinate.suburb);

                // Update the displayed suburb list
                addSuburbToListDOM(coordinate.suburb);

                console.log("Updated list of suburbs: ", addedSuburbNames)
            });
        })
        .catch(error => {
            console.error('Error fetching suburb coordinates:', error);
        });
}

// Function to add a suburb to the DOM list
function addSuburbToListDOM(suburbName) {
    const suburbListContainer = document.getElementById("suburbListContainer");

    const suburbItem = document.createElement('div');
    suburbItem.classList.add('suburb-item');
    suburbItem.innerHTML = `${suburbName} <button data-suburb="${suburbName}">x</button>`;

    // Add click event to remove individual suburb
    suburbItem.querySelector('button').addEventListener('click', function () {
        removeSuburb(suburbName);
    });

    suburbListContainer.appendChild(suburbItem);
}

// Function to remove individual suburb from the map and list
function removeSuburb(suburbName) {
    // Remove the marker from the map
    addedSuburbs = addedSuburbs.filter(suburb => {
        if (suburb.suburb === suburbName) {
            map.removeLayer(suburb.marker);
            return false;
        }
        return true;
    });

    // Remove the suburb from the tracking array
    addedSuburbNames = addedSuburbNames.filter(name => name !== suburbName);

    // Update the displayed list of suburbs
    const suburbListContainer = document.getElementById("suburbListContainer");
    suburbListContainer.innerHTML = '';  // Clear list
    addedSuburbs.forEach(s => {
        addSuburbToListDOM(s.suburb);
    });
}

// Clear all markers from the map
document.getElementById("resetMap").addEventListener("click", function () {
    console.log("Clearing suburbs:", addedSuburbNames)

    markersLayer.clearLayers();
    addedSuburbs = [];
    addedSuburbNames = [];
    document.getElementById("suburbListContainer").innerHTML = '';
});


// Function to send addedSuburbNames to the Flask backend
function sendAddedSuburbNames() {
    fetch('/process_suburb', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ suburbs: addedSuburbNames }), // Send the addedSuburbNames array
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data); // Handle the success response
        //alert('Suburb names sent to backend successfully');
    })
    .catch((error) => {
        console.error('Error:', error); // Handle any errors
        //alert('Failed to send suburb names to the backend');
    });
}

// Example: Call this function when a button is clicked
document.getElementById("finishSelect").addEventListener("click", function () {
    if (addedSuburbNames.length > 0) {
        sendAddedSuburbNames();
    } else {
                alert("Error: No suburbs have been added. Please add a suburb before proceeding.");

    }
});


function updateChartOptions() {
    const variable = document.getElementById("variable").value;
    console.log(variable)

    const chartTypeSelect = document.getElementById("chartType");

    chartTypeSelect.innerHTML = '';

    if (variable === 'temperature' || variable === 'rainfall') {
        const options = [
            { value: 'lineChart', text: 'Line chart' },
            { value: 'barChart', text: 'Bar chart' },
            { value: 'histogram', text: 'Histogram' },
            { value: 'areaChart', text: 'Area chart' },
        ];
        options.forEach(option => {
            const newOption = document.createElement("option");
            newOption.value = option.value;
            newOption.text = option.text;
            chartTypeSelect.appendChild(newOption);
        });
    } 
    
    // Chart options for other variables
    else {
        const defaultOptions = [
            { value: 'lineChart', text: 'Line chart' },
            { value: 'pointChart', text: 'Point chart' },
            { value: 'line_bar_chart', text: 'Combination chart' }
        ];
        defaultOptions.forEach(option => {
            const newOption = document.createElement("option");
            newOption.value = option.value;
            newOption.text = option.text;
            chartTypeSelect.appendChild(newOption);
        });
    }
}


document.getElementById('chartButton').addEventListener('click', function(event) {
    const suburbListContainer = document.getElementById('suburbListContainer');

    if (suburbListContainer.innerHTML.trim() === '') {
        alert("Error: Please enter suburbs into the container first.");
        event.preventDefault(); // Prevent the form submission
    }

    const endDate = document.getElementById('endDate').value;
    const startDate = document.getElementById('startDate').value;
    if (new Date(startDate) >= new Date(endDate)) {
        alert("Start date cannot be after end date");
    }
});

document.getElementById('predictButton').addEventListener('click', function(event) {
    const suburbListContainer = document.getElementById('suburbListContainer');

    if (suburbListContainer.innerHTML.trim() === '') {
        alert("Error: Please enter suburbs into the container first.");
        event.preventDefault(); // Prevent the form submission
    }
});

document.getElementById('endDate').addEventListener('input', function(event) {
    const endDate = document.getElementById('endDate').value;
    const startDate = document.getElementById('startDate').value;
    if (new Date(startDate) >= new Date(endDate)) {
        alert("Start date cannot be after end date");
    }
});




