# Start with the Node base image
FROM node:20

# Set the working directory in the container
WORKDIR /app

# Copy the frontend application files into the container
COPY . /app

# Install the Node.js dependencies
RUN npm install

# Build the project for production
RUN npm run build

# Install `serve` to serve the static files
RUN npm install -g serve

# Expose the port the app runs on
EXPOSE 3000

# Command to run the React application
CMD ["serve", "-s", "build"]
