const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');

const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

const reviewsData = JSON.parse(fs.readFileSync('reviews.json', 'utf8'));
const dealershipsData = JSON.parse(fs.readFileSync('dealerships.json', 'utf8'));

mongoose.connect('mongodb://mongo_db:27017/', { dbName: 'dealershipsDB' });

const Reviews = require('./review');
const Dealerships = require('./dealership');

(async() => {
    try {
        await Reviews.deleteMany({});
        await Reviews.insertMany(reviewsData.reviews);

        await Dealerships.deleteMany({});
        await Dealerships.insertMany(dealershipsData.dealerships);
    } catch (error) {
        console.error('Error initializing the database:', error);
    }
})();

// Express route to home
app.get('/', (req, res) => {
    res.send('Welcome to the Mongoose API');
});

// Express route to fetch all reviews
app.get('/fetchReviews', async(req, res) => {
    try {
        const documents = await Reviews.find();
        res.json(documents);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching documents' });
    }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', async(req, res) => {
    try {
        const documents = await Reviews.find({ dealership: req.params.id });
        res.json(documents);
    } catch (error) {
        res.status(500).json({ error: 'Error fetching documents' });
    }
});

// Express route to fetch all dealerships
app.get('/fetchDealers', async(req, res) => {
    try {
        const dealers = await Dealerships.find();
        res.json(dealers);
    } catch (error) {
        console.error('Error fetching dealers:', error);
        res.status(500).json({ message: 'Error fetching dealers' });
    }
});

// Express route to fetch dealers by a particular state
app.get('/fetchDealers/:state', async(req, res) => {
    try {
        const dealers = await Dealerships.find({ state: req.params.state });
        res.json(dealers);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Express route to fetch dealer by a particular id
app.get('/fetchDealer/:id', async(req, res) => {
    try {
        const dealer = await Dealerships.findOne({ id: req.params.id });
        if (dealer) {
            res.json(dealer);
        } else {
            res.status(404).json({ message: 'Dealer not found' });
        }
    } catch (error) {
        res.status(500).json({ error: 'Error fetching dealer' });
    }
});

// Express route to insert review
app.post('/insert_review', express.raw({ type: '*/*' }), async(req, res) => {
    try {
        const data = JSON.parse(req.body);
        const latestReview = await Reviews.findOne().sort({ id: -1 });
        const newId = latestReview ? latestReview.id + 1 : 1;

        const review = new Reviews({
            id: newId,
            name: data.name,
            dealership: data.dealership,
            review: data.review,
            purchase: data.purchase,
            purchase_date: data.purchase_date,
            car_make: data.car_make,
            car_model: data.car_model,
            car_year: data.car_year,
        });

        const savedReview = await review.save();
        res.json(savedReview);
    } catch (error) {
        console.error('Error inserting review:', error);
        res.status(500).json({ error: 'Error inserting review' });
    }
});

// Start the Express server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});