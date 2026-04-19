class DisplayManager:
    @staticmethod
    def display_fail(senseHat): # Red dots in bottom corners
        senseHat.set_pixel(7, 7, 254, 0, 0)
        senseHat.set_pixel(0, 7, 254, 0, 0)

    @staticmethod
    def display_success(senseHat): # Green dots in bottom corners
        senseHat.set_pixel(7, 7, 0, 254, 0)
        senseHat.set_pixel(0, 7, 0, 254, 0)

    def temperature_colour(temperature):
        if temperature > 40:
            RGB_value = [255, 0, 0]
        elif temperature > 30:
            RGB_value = [255, 90, 0]
        elif temperature > 20:
            RGB_value = [255, 191, 0]
        elif temperature > 10:
            RGB_value = [0, 97, 255]
        elif temperature > 0:
            RGB_value = [0, 0, 255]
        else:
            RGB_value = [255, 255, 255]
        return RGB_value

    def display_environmental_data(temperature, humidity, senseHat):
        RGB_value = DisplayManager.temperature_colour(temperature)
        senseHat.show_message("%sC" % temperature, text_colour=RGB_value)
        senseHat.show_message("%s%%" % humidity)