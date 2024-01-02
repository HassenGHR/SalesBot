notImplemented = "ErrDialog not implemented."

# Corpus file
corpus_d = {'on_start': [
    ["""Welcome to MrSalesBot.
MrSalesBot is here to help you record your sales entries.
MrSalesBot can understand natural language, even voice messages"""],
    [
        "Hello user!!!! I must advise you, to start recording your sales, you must provide some information about you first."]],

    'personal_info': [
        ["Please tell me your name:"],
        ["Very good {name}, Now tell me about the default product category you want to take account for?"],
        ["Okay, I will save {default_product} as your default product category. Is it correct?"],
        ["That is it {name}. Now we can start to take account of all your sales entries."]],

    'personal_info_err': [
        [notImplemented],
        ["I was unable to understand your name. Please try again."],
        ["I was unable to understand your product category. Please try again."],
        ["I am very sorry, please say your default product category again."],
        ["It was a Yes/No answer, and I couldn't figure out your reply. Please try it again."]],

    'actions': [
        ["Please tell me, what do you want to do? You can ask me for help if you need ..."],
        ["{name}, I can't understand the action you want to do, please try it again."]],

    'help': [
        ["""There are a lot of things that I can do for you:
- I can show you your last sales statistics
- I can edit your personal information
- I can add a new sales entry
- I can delete all your data (private and all sales entries)"""]],

    'record': [
        ['Okay {name}, let\'s record your sale.', 'Did you sold any {default_product} today?'],
        ['Please tell me what product did you sold today'],
        ['Please tell me the quantity of the item sold.'],
        ['Please tell me what was the price per unit of the item?'],
        ['Please tell me what is the client\'s  Name?'],
        ['Please tell me what is the client\'s  phone, City?'],
        ['Lastly Could you tell me the status of this product if it is paid or not?'],
        ['I understood you sold {quantity} units of {product_title} at {unit_price} per unit to {client_name}. Is that correct?'],
        ['Great sale, {name}! Your data was saved.']],

    'record_err': [
        [notImplemented],
        ["Sorry {name}, I was unable to understand your yes/no answer. Please try again."],
        ["Sorry {name}, I was unable to understand your sold product. Please try again."],
        ["Sorry {name}, I was unable to understand the quantity. Please try again."],
        ["Sorry {name}, I was unable to understand the price. Please try again."],
        ["Sorry {name}, I was unable to understand the client's contact information. Please try again."],
        ["Sorry {name}, I was unable to understand the status of this payment. Please try again with Yes or No."],
    ],

    'stats': [
        ["Okay, {name}, let's see your sales statistics..."],
        [
            '- product category: {product_category}, last {n_records} days entries.\n- total revenue: {total_revenue}\n- average price: {average_price}\n- total quantity sold: {total_quantity_sold}',
            'This is a great result, keep it up!'],
        ['Sorry {name}, you don\'t have any sales entrie'
         's yet. Please make a sale before asking for stats.']],

    'cancel': [
        ['Okay, canceling the last operation...']],

    'cancel_err': [
        ["Sorry, you cannot cancel this operation.",
         "I can't help you if you don't provide some default information."]],

    'delete': [
        ['I am prepared to delete all your sales data. All your private and sales entries data will be lost.',
         "Still, do you want to proceed?"],
        ['As you wish. Bye-bye {name} !!!'],
        ['Uff!!!, Okay {name}, your data will remain safe.']],

    'delete_err': [
        [notImplemented],
        ["I was unable to understand your yes/no answer. Please try again."]],

    'end': [
        [
            'You have chosen to stop interacting with MrSalesBot. If you want to start interacting again, please send a "/start" command.']]}
