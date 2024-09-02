library(tidyverse)
library(shiny)
library(DBI)
library(RPostgres)
library(tmap)
library(leaflet)
library(sf)

ui <- fluidPage(

    titlePanel("Weather Map"),

    sidebarLayout(
        sidebarPanel = sidebarPanel(
            sliderInput('DatesMerge',
                        'Date', 
                        min = as.Date('1999-12-31',"%Y-%m-%d"), 
                        max = as.Date('2024-07-31',"%Y-%m-%d"), 
                        value = c(as.Date("1999-12-31"), as.Date("2024-07-31")),
                        timeFormat="%Y-%m-%d")
        ), # change to directly get oldest and latest date from data
        mainPanel = mainPanel(leafletOutput(outputId = 'map'))
    )
)

server <- function(input, output){
    # Connect to PostgreSQL and fetch data
    conn <- dbConnect(
        RPostgres::Postgres(),
        dbname = "climatepulse",
        host = "postgres-1.c96iysms626t.ap-southeast-2.rds.amazonaws.com",
        port = 5432,
        user = "postgres",
        password = "Climatepulse123."
    )

    temp_data <- dbGetQuery(conn, "SELECT clusterid, datetime, temperaturemean FROM weatherdata;")
    coordinates <- dbGetQuery(conn, "SELECT clusterid, lattitude, longtitude, officialnamesuburb FROM suburbclustered")

    first_date = dbGetQuery(conn, "SELECT min(datetime) FROM weatherdata;")
    latest_date = dbGetQuery(conn, "SELECT max(datetime) FROM weatherdata")

    print(first_date)
    print(latest_date)

    map_df = reactive({
        temp_data %>%
        filter(datetime > input$DatesMerge[1] & datetime < input$DatesMerge[2]) %>%
        group_by(clusterid) %>%
        summarise(tempavg = mean(temperaturemean)) %>%
        left_join(coordinates, by = "clusterid") %>%
        st_as_sf(coords = c('longtitude', 'lattitude')) %>%
        st_set_crs(4326)
    })

    temp_scale <- reactive({
        colorNumeric(
            palette = colorRampPalette(c("green", "yellow", "red"))(100), 
            domain = range(map_df()$tempavg, na.rm = TRUE) # fix range later 
        )
    })

    output$map = renderLeaflet({
        leaflet() %>%
        addTiles() %>%
        setView(lat = -25.2744, lng = 133.7751, zoom=4) %>%
        addCircleMarkers(
                        data = map_df(), 
                        #radius = ~log10(tempavg + 1) * 10, # remove later
                        color = ~temp_scale()(tempavg),
                        fillOpacity = 0.7,
                        popup = ~paste("Suburb: ", officialnamesuburb, "<br>Average Temperature: ", round(tempavg, 2), "°C")) %>%
        addLegend(
            pal = temp_scale(), 
            values = map_df()$tempavg, 
            title = "Temperature (°C)",
            position = "bottomleft"
        )
    })

    on.exit(dbDisconnect(conn), add = TRUE)
}

shinyApp(ui, server)