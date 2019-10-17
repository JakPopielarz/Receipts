# Receipts
A fairly simple app to analyse and automatically create a database of receipts. This bases on photos.

To achieve the ultimate number recognition a KNNearest algorithm from OpenCV library was employed.

## How to use
- Select a photo to analyze
- Click, hold and drag to select area with the sum (cannot change the selection after releasing LMB)
- approve or rectify the recognition
- choose a date for the receipt, add it to the database
- repeat, if you wish

## Learning
By digging a bit into the code one can disable or enable further deepening of the knowledge-base. All you have to do is comment/uncomment a block of code after a code responsible for pop up asking if the number was recognized correctly (in gui.py).
After building it up a bit the generalsamples.data and generalresponses.data (as I call it - knowledge base) will be shared in this repo.

## Note
I realise that this app is lacking in some aspects, but it was meant just as a thing that would get summing up receipts done for me.

## Development plans
- displaying the photo whilst adding it to database (for ease of for example looking up it's date
- displaying the database from inside the app

# ULTIMATE DEVELOPMENT TARGET:
Fully automatically recognizing the position of the overall sum and it's amount on the receipt.
