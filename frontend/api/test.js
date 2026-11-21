module.exports = (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.json({ ok: true, timestamp: new Date().toISOString() });
};
