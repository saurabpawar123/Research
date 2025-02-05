import React, { useState } from "react";
import './styles.css';  // Import the CSS file

export default function App() {
  const [topic, setTopic] = useState("");
  const [summary, setSummary] = useState(null);  // To store the summary or any status message
  const [loading, setLoading] = useState(false);  // To show the loading state

  // Function to handle the form submission
  const handleSubmit = async () => {
    setLoading(true);  // Start the loading spinner
    setSummary(null);   // Clear previous results

    try {
      // Send a POST request to the Flask backend
      const res = await fetch("http://localhost:5000/run_workflow", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic }),  // Send the topic entered by the user
      });

      // Parse the JSON response
      const data = await res.json();

      // Check if the API returned a successful summary
      if (data.summary) {
        setSummary(data.summary);  // Set the summary
      }

      // Handle errors or status messages if they exist
      if (data.error) {
        setSummary(data.error);  // Set the error message
      }

      if (data.file_status) {
        // If there is a file save status, show it as well
        setSummary((prev) => `${prev ? prev + ' ' : ''}${data.file_status}`);
      }

    } catch (error) {
      // Catch and show any errors that occur while fetching the data
      setSummary("Error running workflow");
    }

    setLoading(false);  // Stop the loading spinner
  };

  return (
    <div className="body">
      {/* Centered White Rectangle Block */}
      <div className="centered-block">
        {/* Company Logo */}
        <img
          src="/assets/logo.png"  // Path to the logo in the public folder
          alt="Company Logo"
          className="company-logo"
        />
        
        <h1>Research Assistant</h1>
        <p>Enter a topic to begin your research</p>

        {/* Input field for topic */}
        <input
          type="text"
          placeholder="Enter research topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />

        {/* Button to trigger research */}
        <button
          onClick={handleSubmit}
          disabled={loading}  // Disable button while loading
        >
          {loading ? "Processing..." : "Start Research"}
        </button>

        {/* Displaying the summary or any error/status messages */}
        {summary && <p className="summary">{summary}</p>}
      </div>
    </div>
  );
}
