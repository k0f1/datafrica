#! /usr/bin/env python3
#from __future__ import unicode_literals


from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item


# Make an instance of create engine
engine = create_engine('sqlite:///catalog.db')

# Bind the engine to the metadata of the Base class
# To establish conversation with the database and act as staging zone
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# Create DB session instance
session = DBSession()


# Items for Fitness Equipment
category1 = Category(name = "Fitness Equipments")

session.add(category1)
session.commit()

item1 = Item(title="Eco Friendly Yoga Matt",
             description="61cm yoga matt", price="£10.60", category=category1)

session.add(item1)
session.commit()


item2 = Item(title = "Hangzhou Biodegradable Matt",
description = "Eco friendly high intensity interval training\n matt at reasonable price. 61cm by 1.5mm thickness", price = "£15.40", category = category1)
session.add(item2)
session.commit()


item3 = Item(title = "Custom Jump Ropes", description = "High intensity interval training jump rope at reasonable price", price = "£5.30", category = category1)
session.add(item3)
session.commit()


item4 = Item(title = "Sweat Resistance Bands", description = "High intensity interval training sweat resistance bands at reasonable price", price = "£5.60", category = category1)
session.add(item4)
session.commit()


# Health and Beauty Aids Category
category1 = Category(name = "Health and Beauty Aids")
session.add(category1)
session.commit()


# Matcha Tea item1
item1 = Item(title = "100% Organic Matcha Tea",  description = "Best quality  japanese food grade Matcha green tea 100g ", price = "£9.99", category = category1)
session.add(item1)
session.commit()

# Matcha Tea item2
item2 = Item(title = "Green Matcha Tea",  description = "Matcha green tea 50g ", price = "£9.99", category = category1)
session.add(item2)
session.commit()


# Beard oil is Item3
item3 = Item(title = "Organic Beard Oil",
description = "100% natural organic mens scented care growth oil for men 100ml", price = "£11.99", category = category1)
session.add(item3)
session.commit()


 # Mobile Phone `Accessories Category
category2 = Category(name = "Phone Acessories")
session.add(category1)
session.commit()

# Mobile phone cases
item1 = Item(title = "For samsung Galaxy 10", description = "Best quality dual mobile Phone Case", price = "£2.50", category = category2)
session.add(item1)
session.commit()


item2 = Item(title = "For Iphone X", description = "Real Saffiano leather mobile phone case for Iphone X", price = "£10.50", category = category2)
session.add(item2)
session.commit()

# Smart Phone Power Banks - lithium batteries is another Item
item3 = Item(title = "Solar Mobile Phone Power Bank", description = "Soler 20000mah mobile phone charger wireless modern sample battery portable power bank for iphone 6/6s", price = "£30.50", category = category2)
session.add(item3)
session.commit()


item4 = Item(title = "Wireless Mobile Phone Power Bank", description = "Qi 8000mAh 10000mah Wireless Charger Power Bank Mobile Phone Charger for iPhone 8 X", price = "£14.99", category = category2)
session.add(item4)
session.commit()


# Camping Category
category3 = Category(name = "Camping")
session.add(category1)
session.commit()

item1 = Item(title = "170T Sleep Bag",  description = "Amazon Hot 170T Polyester Taffeta Lining Soft Hollow Cotton 200gsm (190+30)*75cm Spill Resistant Envelope Camping Sleeping bag", price = "£13.99", category = category3)
session.add(item1)
session.commit()


item2 = Item(title = "190T Tent", description = "190T 2 person outdoor easy folding wholesale waterproof double layer pop up tent", price = "£19.99", category = category3)
session.add(item2)
session.commit()



# Toys, Games and Hobbies Category
category4 = Category(name = "Toys, Games and Hobbies")
session.add(category1)
session.commit()


# Pool Inflatables item
item1 = Item(title = "Giant Pink Flamingo Pool Inflatable", description = "New Design Inflatable Summer Cool Giant Pink Flamingo Swimming Pool Float. Medium Intex - Inflatable Flamingo - 142x137x97 cm)", price = "£4.99", category = category4)
session.add(item1)
session.commit()


# Sports Super Category

# Snowboarding category
category5 = Category(name = "Snowboarding")
session.add(category5)
session.commit()

# Snowboarding items
item1 = Item(title = "Goggles", description = "Dragon XI mirrowed ski goggles measuring height 10.5cm x waist 17cm", price = "$150.00", category = category5)
session.add(item1)
session.commit()

item2 = Item(title = "Snowboard", description = "Best in class quality", price ="£250.00", category = category5)
session.add(item2)
session.commit()


# Football category
category6 = Category(name = "Football")
session.add(category6)
session.commit()

item1 = Item(title = "Jersey", description = "100% Polyester in black and white color", price = "£20.00", category = category6)
session.add(item1)
session.commit()


item2 = Item(title = "Two Shinguards", description = "Best quality shin protection", price = "£5.00", category = category6)
session.add(item2)
session.commit()


item3 = Item(title = "Shinguards", description = "2019 WECDOIT branded Spot goods shinguard high quality soccer shinguard football shinguards", price = "£10.00", category = category6)
session.add(item4)
session.commit()

item4 = Item(title = "Soccer Cleats", description = "2020 top quality new design  football shoes, men outdoor indoor soccer cleats, oem football boots soccer shoes", price = "£30.00", category = category6)
session.add(item4)
session.commit()



category7 = Category(name = "Basketball")
session.add(category7)
session.commit()



category8 = Category(name = "Baseball")
session.add(category8)
session.commit()

item1 = Item(title = "Bat", description = "32 inch Great quality Aluminum ALLOY baseball bat", price = "£10.00", category = category8)
session.add(item1)
session.commit()

category9 = Category(name = "Frisbee")
session.add(category9)
session.commit()

item1 = Item(title = "Frisbee", description = "High end plastic Frisbee indoor and outdoor toys", price = "£5.00", category = category9)
session.add(item1)
session.commit()

category10 = Category(name = "Rock Climbing")
session.add(category10)
session.commit()


category11 = Category(name = "Skating")
session.add(category11)
session.commit()


category12 = Category(name = "Hockey")
session.add(category12)
session.commit()

item1 = Item(title = "Stick", description = "017 Best selling 80% carbon ice hockey sticks with the best quality ", price = "£40.00", category = category12)
session.add(item1)
session.commit()



# Fashion and Apparels Category
category13 = Category(name = "Fashion and Apparels")
session.add(category13)
session.commit()


# Lace Bras
item1 = Item(title = "BEIZHI Lace Bras", description = "BEIZHI 2 piece women lingerie bra set lace bra and panty set underwear", price = "£14.99", category = category13)
session.add(item1)
session.commit()

# Cat Eye Sun Glasses
item2 = Item(title = "Trendy women", description = "Women Trendy Plastic Half Cat Eye Frame Yellow Sunglasses", price = "£5.00", category = category13)
session.add(item2)
session.commit()


item3 = Item(title = "Retro Vintage Cateye", description = "2019 Retro Vintage Cateye Custom Feminino Oculos de Sol Small Triangle Cat Eye Girls Sunglasses Sun Glasses", price = "£7.00", category = category13)
session.add(item3)
session.commit()


print ("added items!")
