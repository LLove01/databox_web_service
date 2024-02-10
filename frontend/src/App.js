import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  // State Variables
  const [repoName, setRepoName] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [githubMetrics] = useState({});
  const [error, setError] = useState('');
  const [userId, setUserId] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [propertyId, setPropertyId] = useState('');
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [showInfoMessage, setShowInfoMessage] = useState(false);
  const [availableMetrics, setAvailableMetrics] = useState({});
  const [selectedMetrics, setSelectedMetrics] = useState(new Set());
  const [databoxAccessToken, setDataboxAccessToken] = useState('');
  const [serverResponseMessage, setServerResponseMessage] = useState('');
  const [fetchInterval, setFetchInterval] = useState(5);
  const [fetchIntervalId, setFetchIntervalId] = useState(null);
  const [periodicInProgress, setPeriodicInProgress] = useState(false);
  const [logs, setLogs] = useState([]);


  // EFFECT HOOKS 

  useEffect(() => {
    const storedMetrics = JSON.parse(localStorage.getItem('combinedMetrics'));
    if (storedMetrics) {
      setAvailableMetrics(storedMetrics);
    }
  }, []);

  useEffect(() => {
    const queryParams = new URLSearchParams(window.location.search);
    const userIdFromUrl = queryParams.get('user_id');
    if (userIdFromUrl) {
      setUserId(userIdFromUrl);
      setIsAuthenticated(true);
      setShowSuccessMessage(true);
      const timer = setTimeout(() => {
        setShowSuccessMessage(false);
        setShowInfoMessage(true);
      }, 5000); // Hide after 5 seconds
      return () => clearTimeout(timer);
    }
  }, []);

  // GITHUB FETCHING 

  const fetchGithubMetrics = async () => {
    setError('');
    try {
      const response = await fetch('http://localhost:8000/fetch-github-metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_name: repoName, github_token: githubToken }),
      });

      if (response.ok) {
        const data = await response.json();
        // Assume the data is an object where keys are metric names and values are the metrics
        const reformattedMetrics = {};
        for (const [key, value] of Object.entries(data)) {
          reformattedMetrics[key] = value;
        }
        saveMetricsToLocalStorage(reformattedMetrics);
      } else {
        // Handle different error codes with specific messages
        let errorDetail = 'Failed to fetch GitHub metrics';
        if (response.status === 404) {
          errorDetail = 'GitHub repository not found.';
        } else if (response.status === 401 || response.status === 403) {
          errorDetail = 'Invalid GitHub token.';
        } else if (response.status === 400) {
          errorDetail = 'Bad request. Please check the repository name and token.';
        }
        else {
          errorDetail = 'Internal server error.';
        }
        // Use errorDetail for specific error feedback
        throw new Error(errorDetail);
      }
    } catch (error) {
      console.error('There was an error!', error);
      setError(error.toString());
    }
  };

  // GOOGLE ANALYTICS AUTHENTICATION AND FETCHING 

  const authenticateGoogleAnalytics = () => {
    const clientId = "122137706214-b7sj6gscpji81pqucanso26677hi2rle.apps.googleusercontent.com";
    const redirectUri = encodeURIComponent("http://localhost:8000/oauth-callback");
    const scope = encodeURIComponent('https://www.googleapis.com/auth/analytics.readonly');
    const responseType = 'code';
    const accessType = 'offline'; // For obtaining a refresh token
    const prompt = 'select_account'; // Forces account selection
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}&response_type=${responseType}&access_type=${accessType}&prompt=${prompt}`;

    window.location.href = authUrl;
  };

  const handlePropertyIdSubmit = async (e) => {
    e.preventDefault();
    if (!userId) {
      setError('User ID is missing. Please ensure you are authenticated.');
      return;
    }

    try {
      setError('');
      const response = await fetch('http://localhost:8000/fetch-analytics-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, property_id: propertyId }),
      });

      if (response.ok) {
        const data = await response.json();

        if (data.error) {
          setError(data.error);
        } else {
          const reformattedData = data.gaData.rows.reduce((formattedData, row) => {
            row.metrics.forEach((metricValue, index) => {
              const metricHeader = data.gaData.metricHeaders[index];
              formattedData[metricHeader] = parseInt(metricValue, 10) || 0;
            });
            return formattedData;
          }, {});
          saveMetricsToLocalStorage(reformattedData);
          console.log('Reformatted Google Analytics Data:', reformattedData);
        }
      } else {
        const errorData = await response.json();
        switch (response.status) {
          case 401:
            setError("Authentication failed. Please check your credentials.");
            break;
          case 404:
            setError("The specified Google Analytics property ID was not found.");
            break;
          case 403:
            setError("Access denied. You do not have permission to access this Google Analytics property.");
            break;
          default:
            setError(errorData.error || "An unknown error occurred while fetching Google Analytics data.");
        }
      }
    } catch (error) {
      console.error('Error fetching the Google Analytics data:', error);
      setError("An error occurred while processing your request. Please try again later.");
    }
  };

  // LOCAL STORAGE 

  const handleClearLocalStorage = () => {
    localStorage.clear();
    setAvailableMetrics({});
    setSelectedMetrics(new Set());
    console.log('Local storage cleared.');
  };

  const saveMetricsToLocalStorage = (newMetrics) => {
    // Merge with existing metrics in local storage
    const existingMetrics = JSON.parse(localStorage.getItem('combinedMetrics')) || {};
    const combinedMetrics = { ...existingMetrics, ...newMetrics };
    localStorage.setItem('combinedMetrics', JSON.stringify(combinedMetrics));
    setAvailableMetrics(combinedMetrics); // Update state to trigger re-render
  };

  // METRICS HANDLING 

  const handleMetricSelectionChange = (metric, isChecked) => {
    setSelectedMetrics((prevSelectedMetrics) => {
      const newSelectedMetrics = new Set(prevSelectedMetrics);
      if (isChecked) {
        newSelectedMetrics.add(metric);
      } else {
        newSelectedMetrics.delete(metric);
      }
      return newSelectedMetrics;
    });
  };

  const submitMetrics = async () => {
    // Ensure Databox access token is provided
    if (!databoxAccessToken.trim()) {
      setError("Please provide the Databox access token.");
      return;
    }
    const payload = {
      metrics: Array.from(selectedMetrics).map(metricName => ({
        name: metricName,
        value: availableMetrics[metricName]
      })),
      databox_access_token: databoxAccessToken,
    };

    try {
      const response = await fetch('http://localhost:8000/send-metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Unable to send metrics. Please check metrics and token.');
      }

      const responseData = await response.json();
      setServerResponseMessage(responseData.message);
      setTimeout(() => setServerResponseMessage(''), 5000);
    } catch (error) {
      setError(error.toString());
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleSubmitSelectedMetrics = async (e) => {
    e.preventDefault();
    await submitMetrics();
  };

  const isMetricsListEmpty = () => Object.keys(availableMetrics).length === 0;

  // MOCK DATA 

  const generateMockData = () => {
    localStorage.removeItem('combinedMetrics');
    const mockData = {
      'Total Revenue': 1500000,
      'Net Profit': 300000,
      'Customer Acquisition Cost': 500,
      'Customer Lifetime Value': 2000,
      'Conversion Rate': 0.05,
      'Average Order Value': 100,
      'Churn Rate': 0.1,
      'Return on Investment (ROI)': 0.2,
    };
    localStorage.setItem('combinedMetrics', JSON.stringify(mockData));
    setAvailableMetrics(mockData);
  };

  // PERIODIC FETCHING AND SENDING FUNCTIONS 

  const handleIntervalChange = (event) => {
    setFetchInterval(parseInt(event.target.value));
  };

  const handlePeriodicFetch = () => {
    if (periodicInProgress) {
      clearInterval(fetchIntervalId);
      setPeriodicInProgress(false);
    } else {
      const fetchAndSubmitMetrics = async () => {
        try {
          localStorage.clear();
          await fetchGithubMetrics();

          const allMetrics = new Set(Object.keys(availableMetrics));
          setSelectedMetrics(allMetrics);

          await submitMetrics();
        } catch (error) {
          console.error("Error in periodic fetch and submit:", error);
          clearInterval(fetchIntervalId);
          setPeriodicInProgress(false);
          setError(error.message || "An error occurred during periodic fetch and submit.");
          return;
        }
      };

      fetchAndSubmitMetrics();
      const intervalId = setInterval(() => {
        fetchAndSubmitMetrics();
      }, fetchInterval * 60 * 1000);

      setFetchIntervalId(intervalId);
      setPeriodicInProgress(true);
    }
  };

  // FETCHING LOGS

  const fetchLogs = async () => {
    try {
      const response = await fetch('http://localhost:8000/fetch-logs');
      if (!response.ok) {
        throw new Error('Failed to fetch logs');
      }
      const data = await response.json();
      setLogs(data);
    } catch (error) {
      console.error('Error fetching logs:', error);
      alert('Failed to fetch logs. Check console for more details.');
    }
  };

  // JSX CODE 

  return (
    <div className="container">
      {error && <p className="error-message">{error}</p>}

      <h1>DataBox Service Exercise</h1>

      {/* GitHub Data Section */}
      <section className="section">
        <h2>GitHub Data</h2>
        <div className="input-group">
          <input
            type="text"
            placeholder="GitHub Repo Name"
            value={repoName}
            onChange={(e) => setRepoName(e.target.value)}
            disabled={periodicInProgress}
          />
          <input
            type="text"
            placeholder="GitHub Token"
            value={githubToken}
            onChange={(e) => setGithubToken(e.target.value)}
            disabled={periodicInProgress}
          />

          <button
            className="button"
            onClick={fetchGithubMetrics}
            disabled={!repoName.trim() || !githubToken.trim() || periodicInProgress}
          >
            Fetch Metrics
          </button>

        </div>
        {Object.keys(githubMetrics).length > 0 && (
          <div className="metrics">
            {Object.entries(githubMetrics).map(([key, value]) => (
              <p key={key}>{`${key.charAt(0).toUpperCase() + key.slice(1)}: ${value}`}</p>
            ))}
          </div>
        )}
      </section>

      {/* Google Analytics Data Section */}
      <section className="section">
        <h2>Google Analytics Data</h2>
        {isAuthenticated ? (
          <div className="input-group">
            {showSuccessMessage && (
              <p className="success-message">Authentication successful.</p>
            )}
            {showInfoMessage && (
              <p className="info-message">
                To fetch Google Analytics data, please enter your Property ID.
                You can find this ID in your Google Analytics account under Admin /
                Property Settings. It's required to access your analytics data.
              </p>
            )}
            <form onSubmit={handlePropertyIdSubmit} disabled={periodicInProgress}>
              <input
                type="text"
                placeholder="Property ID"
                value={propertyId}
                onChange={(e) => setPropertyId(e.target.value)}
                disabled={periodicInProgress}
              />
              <button
                className="button"
                type="submit"
                disabled={!propertyId.trim() || periodicInProgress}
              >
                Submit
              </button>

            </form>
          </div>
        ) : (
          <button className="button" disabled={periodicInProgress} onClick={authenticateGoogleAnalytics}>Access Google Analytics Data</button>
        )}
      </section>
      {/* Available Metrics Section */}
      <section className="section">
        <h2>Available Metrics</h2>
        <button
          className="button"
          onClick={generateMockData}
          disabled={periodicInProgress}
        >
          Load Demo Data
        </button>
        <div className="input-group">
          <form onSubmit={handleSubmitSelectedMetrics}>
            <table className="metrics-table">
              <tbody>
                {Object.entries(availableMetrics).map(([key, value]) => (
                  <tr key={key}>
                    <td>
                      <label>
                        <input
                          type="checkbox"
                          checked={selectedMetrics.has(key)}
                          onChange={(e) => handleMetricSelectionChange(key, e.target.checked)}
                        />
                        {key}
                      </label>
                    </td>
                    <td>{value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <input
              type="text"
              placeholder="Databox Access Token"
              value={databoxAccessToken}
              onChange={(e) => setDataboxAccessToken(e.target.value)}
              style={{ marginTop: '20px' }}
              disabled={periodicInProgress}
            />

            <div className="button-group">
              <button
                type="submit"
                className="submit-button"
                disabled={selectedMetrics.size < 3 || selectedMetrics.size > 5 || databoxAccessToken.trim() === '' || periodicInProgress}
              >
                Submit Selected Metrics
              </button>

              <button
                type="button"
                className="clear-button"
                onClick={handleClearLocalStorage}
                disabled={isMetricsListEmpty() || periodicInProgress}
              >
                Clear Local Storage
              </button>
            </div>
          </form>
        </div>
        {/* Periodic Fetch Section */}
        <section className="section">
          <h2>Periodic Fetch & Push - only for GitHub data</h2>
          <div className="input-group">
            <button
              className={`periodic-fetch-button ${(!repoName.trim() || !githubToken.trim() || !databoxAccessToken.trim()) ? 'disabled' : ''}`}
              onClick={() => {
                handlePeriodicFetch();
              }}
              disabled={!repoName.trim() || !githubToken.trim() || !databoxAccessToken.trim()}
            >
              {periodicInProgress ? "Stop periodic trigger" : "Start periodic trigger"}
            </button>
            <select value={fetchInterval} onChange={handleIntervalChange}>
              <option value={1}>1 Minute</option>
              <option value={5}>5 Minutes</option>
              <option value={60}>1 Hour</option>
              <option value={1440}>1 Day</option>
            </select>
          </div>
        </section>
        {/* Logs display section */}
        <section className="section">
          <h2>Logs</h2>
          <button className='button' onClick={fetchLogs}>Fetch Logs</button>
          <button className='button' onClick={() => setLogs([])}>Clear Logs</button>
          <p className="info-message">The log entries displayed here are retrieved directly from the server's database - only for demonstration purposes.</p>
          <div className="logs-container" style={{ maxHeight: '300px', overflowY: 'auto', marginTop: '20px', border: '1px solid #ccc', padding: '10px' }}>
            {logs.length > 0 ? (
              logs.map((log, index) => (
                <pre key={index}>{JSON.stringify(log, null, 2)}</pre>
              ))
            ) : (
              <p>No logs to display.</p>
            )}
          </div>
        </section>


        {/* Server Response Message Section */}
        {serverResponseMessage && (
          <div className="server-response">
            <p>{serverResponseMessage}</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default App;