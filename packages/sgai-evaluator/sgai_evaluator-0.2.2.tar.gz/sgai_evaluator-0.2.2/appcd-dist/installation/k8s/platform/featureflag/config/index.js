'use strict';

const unleash = require('unleash-server');
const enableGoogleOauth = require('./google-auth-hook');

unleash.start({
    authentication: {
        type: 'custom',
        customAuthHandler: enableGoogleOauth,
    },
})
