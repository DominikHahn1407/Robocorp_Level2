from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """ Orders robots from RobotSpareBin Industries Inc. Saves the order HTML receipt as a PDF file. Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt. Creates ZIP archive of the receipts and the images. """
    open_robot_order_website()
    orders = get_orders()
    write_orders(orders)
    archive_receipts()

def open_robot_order_website():
    """Open the Robot Order Website"""
    browser.configure(
        slowmo=100,
    )
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders():
    """Get the orders.csv and return it as a table"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", target_file="input/orders.csv", overwrite=True)
    tables = Tables()
    csv_table = tables.read_table_from_csv(path="input/orders.csv", header=True)
    return csv_table

def got_to_orders():
    """Moves to the order page of the website"""
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(order):
    """Fill the order form for each entry of the data"""
    got_to_orders()

    page = browser.page()
    page.select_option("#head", order["Head"])
    page.check(f"#id-body-{order['Body']}")
    page.fill(".form-control", order["Legs"])
    page.fill("#address", order["Address"])
    page.click("#preview")
    page.click("#order")

    while not page.query_selector("#order-another"):
        page.click("#order")

    store_receipt_as_pdf(order["Order number"])

    page.click("#order-another")
    
def write_orders(orders):
    """Takes the orders and enters them to the website"""
    for row in orders:
        fill_the_form(row)

def store_receipt_as_pdf(order_number):
    """Store the receipt as PDF file for a given order number"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f"output/receipts/{order_number}.pdf")

    image = page.query_selector("#robot-preview-image")
    image.screenshot(path=f"output/receipts/{order_number}.png")

    pdf.add_files_to_pdf(files=[f"output/receipts/{order_number}.png"], target_document=f"output/receipts/{order_number}.pdf", append=True)

def archive_receipts():
    """Archive the receipts into the output folder"""
    folder = Archive()
    folder.archive_folder_with_zip('output/receipts', 'output/orders.zip', include="*.pdf")