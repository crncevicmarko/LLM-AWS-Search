const { CognitoJwtVerifier } = require("aws-jwt-verify");

function generatePolicy(principalId, effect, resource) {
    return {
      principalId,
      policyDocument: {
        Version: "2012-10-17",
        Statement: [
          {
            Effect: "Allow",
            Action: "execute-api:Invoke",
            Resource: [`${resource.split('/')[0]}/*`],
        },
        ],
      },
      context: {
        user: principalId,
      },
    };
  }

exports.handler = async function (event) {
    console.log("Event:", JSON.stringify(event));

    const authHeader = event.authorizationToken;
    console.log("Auth Header:", authHeader);

    if (!authHeader) {
        console.log("No auth header");
        return {
            statusCode: 401,
            isAuthorized: false,
            body: JSON.stringify({ message: "No authorization header found" }),
        };
    }

    const token = authHeader.split(" ")[1];

    const userPoolId = process.env.USER_POOL_ID;
    const clientId = process.env.CLIENT_ID;
    console.log("Token: ", token);

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

    return generatePolicy(payload.sub, "Allow", event.methodArn);
};
