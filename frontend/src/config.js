const BACKEND_PROTOCOL = 'http';
const BACKEND_DOMAIN = 'localhost';
const BACKEND_PORT = '5000';
const BACKEND_BASE_ROUTE = `${BACKEND_PROTOCOL}://${BACKEND_DOMAIN}:${BACKEND_PORT}`;

export default function getBackendURI(){
    return BACKEND_BASE_ROUTE
}

