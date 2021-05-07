import socket
import json
import requests
import re
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.scrolledtext as st

TITLE_FONT = ("Verdana", 15)
LARGE_FONT = ("Verdana", 11)

URL = "http://127.0.0.1:9876"

user_email_tag = ""
user_url_tag = ""


class PriceTracker(tk.Tk):
    """
    A class to create a bunch of frames

    ...

    Attributes
    ----------
    tk.Tk:
        inherting tkinter module

    Methods
    -------
    show_frame(self, cont):
        function to bring a frame of our choosing
    """

    def __init__(self, *args, **kwargs):
        # initialising the inherited module
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.wm_title(self, "Product Price Tracker")

        container = tk.Frame(self)
        # container, which will be filled with a bunch of frames
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for frames in (LoginPage, HomePage, TrackedProducts, TrackingOptions):

            frame = frames(container, self)
            self.frames[frames] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def show_frame(self, container):

        frame = self.frames[container]
        frame.tkraise()


class LoginPage(tk.Frame):
    """
    A class to create Login page Frame

    ...

    Attributes
    ----------
    tk.Frame:
        inherting Frame from tkinter module
    parent:
        represents a widget to act as the parent of the current object
    controller:
        to interact with another page

    Methods
    -------
    validate_all_fields(self):
        to validate the input fields in login page
    function_list(self):
        list of functions to be called on clicking login button
    validate_phoneno(self, user_phoneno):
        function to validate the phone number
    email_validation(self, user_mail):
        function to validate the mail
    send_login(self, dictionary):
        function to share login details with server
    """

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.flag = 0
        self.login = 0

        label = ttk.Label(self, text="Login Page", font=TITLE_FONT)
        label.grid(row=0, column=2, padx=(10), pady=10, sticky="nsew")

        user_label = ttk.Label(self, text="User Name: ", font=LARGE_FONT).grid(
            row=2, column=1, padx=(10), pady=10
        )
        self.user_name = tk.StringVar()
        username_entry = ttk.Entry(self, textvariable=self.user_name).grid(
            row=2, column=2, padx=(10), pady=10
        )

        email_label = ttk.Label(self, text="Mail: ", font=LARGE_FONT).grid(
            row=3, column=1, padx=(10), pady=10
        )
        self.user_mail = tk.StringVar()
        usermail_entry = ttk.Entry(self, textvariable=self.user_mail).grid(
            row=3, column=2, padx=(10), pady=10
        )

        phone_label = ttk.Label(self, text="Phone Number: ", font=LARGE_FONT).grid(
            row=4, column=1, padx=(10), pady=10
        )
        self.phone_no = tk.StringVar()
        valid_phoneno = self.register(self.validate_phoneno)
        phoneno_entry = ttk.Entry(
            self,
            textvariable=self.phone_no,
            validate="key",
            validatecommand=(valid_phoneno, "%P"),
        ).grid(row=4, column=2, padx=(10), pady=10)

        button = tk.Button(
            self,
            text="Login",
            background="red",
            fg="white",
            command=lambda: self.function_list(),
        )
        button.grid(row=5, column=2, padx=(10), pady=10)

    def validate_all_fields(self):
        global user_email_tag
        if self.user_name.get() == "":
            messagebox.showinfo("Information", "Please Enter Fullname to proceed")
        elif self.phone_no.get() == "":
            messagebox.showinfo("Information", "Please enter Phone Number to proceed")
        elif len(self.phone_no.get()) != 10:
            messagebox.showinfo(
                "Information", "Please Enter 10 digit Phone Number to Proceed"
            )
        elif self.user_mail.get() == "":
            messagebox.showinfo("Information", "Please enter Email to proceed")
        elif self.user_mail.get() != "":
            status = self.email_validation(self.user_mail.get())
            if status:
                self.flag = 1
                user_email_tag = self.user_mail.get()
                self.email = self.user_mail.get()
        else:
            self.flag = 1
            user_email_tag = self.user_mail.get()
            self.email = self.user_mail.get()

    def function_list(self):
        self.validate_all_fields()
        if self.flag == 1:
            dictionary = dict()
            dictionary["name"] = self.user_name.get()
            dictionary["email"] = self.user_mail.get()
            dictionary["phonenumber"] = self.phone_no.get()
            self.send_login(dictionary)
            if self.login == 1:
                self.controller.show_frame(HomePage)

    def validate_phoneno(self, user_phoneno):
        if user_phoneno.isdigit():
            return True
        elif user_phoneno == "":
            return True
        else:
            messagebox.showinfo(
                "Information", "Only Digits are allowed for Phone Number"
            )
            return False

    def email_validation(self, user_mail):
        if len(user_mail) > 7:
            if (
                re.match(
                    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", user_mail
                )
                != None
            ):
                return True
            return False
        else:
            messagebox.showinfo("Information", "This is not a valid email address")
            return False

    def send_login(self, dictionary):
        response = requests.post(URL + "/api/v1/resources/login", data=dictionary)
        if response.text == "User added":
            self.login = 1
            messagebox.showinfo("Information", "User Logged in successfully")
        else:
            messagebox.showinfo(
                "Information", "some error occurred in login. Please try again"
            )


class HomePage(tk.Frame):
    """
    A class to create Home page frame

    ...

    Attributes
    ----------
    tk.Frame:
        inherting frame from tkinter module

    Methods
    -------
    search_button(self, product_url):
        to send url details to server
    validate_url(self):
        to validate user url
    """

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        home_label = ttk.Label(self, text="Home Page", font=TITLE_FONT)
        home_label.grid(row=0, column=2, pady=10, padx=10)
        self.flag = 0

        self.controller = controller

        url_label = ttk.Label(self, text="Product Url: ", font=LARGE_FONT).grid(
            row=2, column=1, padx=(10), pady=10
        )
        self.product_url = tk.StringVar()
        producturl_entry = ttk.Entry(self, textvariable=self.product_url).grid(
            row=2, column=2, padx=(10), pady=10
        )

        button_search = ttk.Button(
            self,
            text="Search",
            command=lambda: self.search_button(self.product_url.get()),
        )
        button_search.grid(row=3, column=1, padx=(10), pady=10)

        button_favourite = ttk.Button(
            self, text="Add To Favourites", command=lambda: self.validate_url()
        )
        button_favourite.grid(row=3, column=2, padx=(10), pady=10)

        button_track = ttk.Button(
            self, text="Track", command=lambda: controller.show_frame(TrackedProducts)
        )
        button_track.grid(row=3, column=3, padx=(10), pady=10)

    def search_button(self, product_url):
        if product_url == "":
            messagebox.showinfo("Information", "Please Enter proper Url to proceed")
        else:
            response = requests.get(URL + "/api/v1/search", data=product_url)
            text_area = st.ScrolledText(
                self, width=30, height=8, font=("Times New Roman", 15)
            )
            text_area.grid(row=4, column=1, padx=20, pady=5)
            response_data = response.json()
            text_area.insert(
                tk.INSERT,
                f'Product: {response_data["Title"]}\n\nPrice: {response_data["Price"]}',
            )
            text_area.configure(state="disabled")

    def validate_url(self):
        global user_url_tag
        if self.product_url.get() == "":
            messagebox.showinfo("Information", "Please Enter Url to proceed")
        else:
            user_url_tag = self.product_url.get()
            self.controller.show_frame(TrackingOptions)


class TrackingOptions(tk.Frame):
    """
    A class to create Tracking option frame

    ...

    Attributes
    ----------
    tk.Frame:
        inherting frame from tkinter module

    Methods
    -------
    validate_all_fields(self):
        to validate the input fields in login page
    add_to_fav(self):
        to send prodcut details to server

    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.flag = 0
        self.controller = controller
        label_title = ttk.Label(self, text="Tracking Options", font=TITLE_FONT)
        label_title.grid(row=0, column=2, pady=10, padx=10)

        label_interval = ttk.Label(self, text="Select Interval: ", font=LARGE_FONT)
        label_interval.grid(row=1, column=1, pady=10, padx=10)

        self.product_interval = tk.StringVar()
        self.product_interval.set("Click Me")

        interval = tk.OptionMenu(self, self.product_interval, "1 Hour", "1 Day")
        interval.grid(row=1, column=2, pady=10, padx=10)

        price_label = ttk.Label(self, text="  Enter Price: ", font=LARGE_FONT).grid(
            row=2, column=1, padx=(10), pady=10
        )
        self.price = tk.StringVar()
        price_entry = ttk.Entry(self, textvariable=self.price).grid(
            row=2, column=2, padx=(10), pady=10
        )

        button_home = ttk.Button(
            self, text="Home Page", command=lambda: controller.show_frame(HomePage)
        )
        button_home.grid(row=3, column=1, padx=(10), pady=10)

        button_cart = ttk.Button(
            self, text="Add to Cart", command=lambda: self.validate_all_fields()
        )
        button_cart.grid(row=3, column=2, padx=(10), pady=10)

    def validate_all_fields(self):
        if self.product_interval.get() == "Click Me":
            messagebox.showinfo("Information", "Please Select Interval to proceed")
        elif self.price.get() == "":
            messagebox.showinfo("Information", "Please Enter Price to Proceed")
        else:
            if self.product_interval.get() == "1 Hour":
                self.product_interval_flag = "0"
            else:
                self.product_interval_flag = "1"
            self.add_to_fav()
            if self.flag == 1:
                self.controller.show_frame(TrackedProducts)

    def add_to_fav(self):
        user_mail = user_email_tag
        user_product_url = user_url_tag
        data = {
            "email": user_mail,
            "interval": self.product_interval_flag,
            "price": self.price.get(),
            "url": user_product_url,
        }
        response = requests.post(URL + "/api/v1/resources/add_t0_fav", data=data)
        if response.text == "Added":
            self.flag = 1
            messagebox.showinfo("Information", "Product added successfully")
        else:
            messagebox.showinfo("Information", "Some error occured Please try again")


class TrackedProducts(tk.Frame):
    """
    A class to create tracked products frame

    ...

    Attributes
    ----------
    tk.Frame:
        inherting frame from tkinter module

    Methods
    -------
    track_button(self):
        to receive tracked products detail from server
    """

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label_title = ttk.Label(self, text="Tracked Products", font=TITLE_FONT)
        label_title.grid(row=0, column=1, pady=10, padx=10)

        button_home = ttk.Button(
            self, text="Home Page", command=lambda: controller.show_frame(HomePage)
        )
        button_home.grid(row=2, column=2, pady=10, padx=10)

        button_tracked = ttk.Button(
            self, text="List Products", command=lambda: self.track_button()
        )
        button_tracked.grid(row=2, column=1, padx=(10), pady=10)

    def track_button(self):

        response = requests.get(URL + "/api/v1/resources/track", data=user_email_tag)
        json_incoming_files = json.loads(response.text)
        text_area = st.ScrolledText(
            self, width=30, height=8, font=("Times New Roman", 15)
        )
        text_area.grid(row=1, column=1, padx=20, pady=5)
        text_area.insert(tk.INSERT, json_incoming_files)
        text_area.configure(state="disabled")


if __name__ == "__main__":
    app = PriceTracker()
    app.mainloop()
