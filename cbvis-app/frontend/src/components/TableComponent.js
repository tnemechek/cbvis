import React, { useEffect, useState, useCallback } from 'react';
import axiosInstance from './axiosInstance'; // Import the axios instance
import BatchLoader from './BatchLoader';
import './TableComponent.css';

const TableComponent = () => {
    const [data, setData] = useState({});
    const [selectedSeries, setSelectedSeries] = useState([]);
    const [seriesDetails, setSeriesDetails] = useState({});
    const [error, setError] = useState('');
    const [navbarCollapsed, setNavbarCollapsed] = useState(false);

    const loadObservationValues = useCallback(async (seriesId) => {
        try {
            const response = await axiosInstance.get('/api/series_values', { params: { series_id: seriesId } });
            setData(prevData => {
                const newData = { ...prevData };
                response.data.forEach(({ date, value }) => {
                    if (!newData[date]) {
                        newData[date] = {};
                    }
                    newData[date][seriesId] = value;
                });
                return newData;
            });
        } catch (error) {
            setError(`Error fetching data: ${error.message}`);
        }
    }, []);

    const handleSeriesSelected = (seriesId) => {
        if (selectedSeries.includes(seriesId)) {
            setSelectedSeries(selectedSeries.filter(id => id !== seriesId));
            setData(prevData => {
                const newData = { ...prevData };
                Object.keys(newData).forEach(date => {
                    delete newData[date][seriesId];
                });
                return newData;
            });
        } else {
            setSelectedSeries([...selectedSeries, seriesId]);
            loadObservationValues(seriesId);
        }
    };

    const onSeriesNamesLoaded = (names) => {
        const details = {};
        names.forEach(name => {
            details[name.series_id] = name.series_name;
        });
        setSeriesDetails(prevDetails => ({ ...prevDetails, ...details }));
    };

    const getSelectedSeriesNames = () => {
        return selectedSeries.map(seriesId => seriesDetails[seriesId] || seriesId);
    };

    const renderTableHeader = () => {
        const headers = ["Date", ...getSelectedSeriesNames()];
        return (
            <thead>
                <tr>
                    {headers.map((header, index) => (
                        <th key={index} style={{ width: '150px', whiteSpace: 'normal' }}>{header}</th>
                    ))}
                </tr>
            </thead>
        );
    };

    const renderTableBody = () => {
        const dates = Object.keys(data);
        return (
            <tbody>
                {dates.map(date => (
                    <tr key={date}>
                        <td style={{ width: '150px', whiteSpace: 'normal' }}>{date}</td>
                        {selectedSeries.map(seriesId => (
                            <td key={seriesId} style={{ width: '150px', whiteSpace: 'normal' }}>{data[date][seriesId] || "-"}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        );
    };

    const toggleNavbar = () => {
        setNavbarCollapsed(!navbarCollapsed);
    };

    return (
        <div className={`table-component-container ${navbarCollapsed ? 'navbar-collapsed' : ''}`}>
            <div className="navbar">
                <button onClick={toggleNavbar}>{navbarCollapsed ? '►' : '◄'}</button>
            </div>
            <div className="table-container">
                <h1>Data Table</h1>
                {error && <div className="error">{error}</div>}
                {Object.keys(data).length > 0 ? (
                    <table>
                        {renderTableHeader()}
                        {renderTableBody()}
                    </table>
                ) : (
                    <p>No data available</p>
                )}
            </div>
            <div className="sidebar">
                <BatchLoader onSeriesNamesLoaded={onSeriesNamesLoaded} onSeriesSelected={handleSeriesSelected} />
                <h2>Selected Series</h2>
                <ul>
                    {selectedSeries.map((seriesId) => (
                        <li key={seriesId} onClick={() => handleSeriesSelected(seriesId)}>
                            {seriesDetails[seriesId]}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

export default TableComponent;
