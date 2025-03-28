# System architecture

## Architecture Overview
The system is structured as follows:

1. **User Input Handling**: Users interact with the chatbot through a frontend single-page application (SPA).
2. **Frontend Application**:
   - Hosted on **AWS S3** and delivered via **AWS CloudFront**.
   - Calls APIs to process user queries and retrieve ticket information.
3. **API Gateway**:
   - Manages API calls between the frontend and backend services.
4. **AWS Lambda Functions**:
   - **getTickets**:
     - Lambda function fetches all Jira tickets using the Jira API.
     - Saves them into Pinecone DB
     - **updateTickets**:
     - Listens to Jira Webhooks for real-time updates (ticket creation, update, comment addition).
     - Saves newly created or updated tickets and comments.
   - **retrieveUserInput**:
     - A dedicated Lambda function embeds user input and finds related Jira tickets.
     - The function also processes and retrieves relevant tickets using vector search.
5. **Vector Search and Similarity Matching**:
   - Uses **Amazon Bedrock** to embed ticket data and user queries.
   - **Pinecone** is used as a vector database to perform similarity searches.
6. **Storage & Hosting**:
   - The frontend assets are stored in an **AWS S3** bucket.
   - The application is served through a **CloudFront distribution**.

## Workflow
1. Users interact with the chatbot via the web application.
2. The frontend sends API requests to the backend via **API Gateway**.
3. The backend processes user queries:
   - Embeds the query using **Amazon Bedrock**.
   - Searches for similar Jira tickets using **Pinecone**.
4. If a relevant ticket exists, it is retrieved and returned to the user.
5. Jira ticket data is fetched and updated in real-time using Jira APIs and Webhooks.
6. The frontend displays the retrieved ticket information to the user.

## Technologies Used
- **Frontend**: Angular (SPA), AWS S3, CloudFront
- **Backend**: AWS Lambda, API Gateway
- **AI Processing**: Amazon Bedrock (embedding), Pinecone (vector search)
- **Jira Integration**: Jira API, Jira Webhooks
