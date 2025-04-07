const { CognitoJwtVerifier } = require("aws-jwt-verify");

function generatePolicy(principalId) {
    return {
        isAuthorized: true,
        context: { user: principalId },
    };
}

exports.handler = async function (event) {
    console.log("Event:", JSON.stringify(event));

    const authHeader = event.headers.authorization;
    console.log("Auth Header:", authHeader);

    // Provera da li postoji authorization header
    if (!authHeader) {
        console.log("No auth header");
        return {
            statusCode: 401,
            isAuthorized: false,
            body: JSON.stringify({ message: "No authorization header found" }),
        };
    }

    const token = authHeader.split(" ")[1];

    // Pristupanje konfiguraciji korisničkog pool-a i client ID-u iz env varijabli
    const userPoolId = process.env.USER_POOL_ID;
    const clientId = process.env.CLIENT_ID;
    console.log("Token: ", token);

    // Kreiranje Cognito verifiera za verifikaciju tokena
    const verifier = CognitoJwtVerifier.create({
        userPoolId: userPoolId,
        tokenUse: "access",
        clientId: clientId,
    });

    let payload;
    try {
        payload = await verifier.verify(token);
        console.log("Token is valid. Payload:", payload);
    } catch (error) {
        console.log("Token not valid!", error);
        return {
            statusCode: 401,
            isAuthorized: false,
            body: JSON.stringify({ message: "Invalid token" }),
        };
    }

    return generatePolicy(payload.sub);
};
