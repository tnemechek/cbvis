import React, { useState, useEffect, useCallback } from 'react';
import { Route, Routes, Link } from 'react-router-dom';
import axios from 'axios';
import debounce from 'lodash.debounce';
import TableComponent from './TableComponent';
import ChartPage from './ChartPage';
import MapPage from './MapPage';
import './Dashboard.css';

const Dashboard = () => {
    const [selectedView, setSelectedView] = useState('table');
    const [filters, setFilters] = useState({
        seasonal_adjustment: [],
        source_name: [],
        release_name: []
    });
    const [filterOptions, setFilterOptions] = useState({
        seasonal_adjustment: [],
        source_name: [],
        release_name: []
    });
    const [searchTerms, setSearchTerms] = useState({
        seasonal_adjustment: '',
        source_name: '',
        release_name: ''
    });

    useEffect(() => {
        axios.get('/api/filter_options')
            .then(response => setFilterOptions(response.data))
            .catch(error => console.error("Error fetching filter options", error));
    }, []);

    const handleSelection = (view) => {
        setSelectedView(view);
    };

    const debouncedFetchFilteredSeries = useCallback(
        debounce((updatedFilters) => {
            setFilters(updatedFilters);
        }, 300), // Adjust the delay as needed
        []
    );

    const handleFilterChange = (filterName, values) => {
        const updatedFilters = {
            ...filters,
            [filterName]: values
        };
        debouncedFetchFilteredSeries(updatedFilters);
    };

    const handleSearchChange = (filterName, searchTerm) => {
        setSearchTerms({
            ...searchTerms,
            [filterName]: searchTerm
        });
    };

    return (
        <div>
            <div className="dash-bar">
                <h2>Data Dashboard</h2>
                <div className="view-selection">
                    <Link to="/dashboard/table" onClick={() => handleSelection('table')}>
                        Table
                    </Link>
                    <Link to="/dashboard/chart" onClick={() => handleSelection('chart')}>
                        Chart
                    </Link>
                    <Link to="/dashboard/map" onClick={() => handleSelection('map')}>
                        Map
                    </Link>
                </div>
                <div className="filters">
                    {['seasonal_adjustment', 'source_name', 'release_name'].map(filter => (
                        <div key={filter} className="filter">
                            <input
                                type="text"
                                placeholder={`Search ${filter.replace('_', ' ')}`}
                                value={searchTerms[filter]}
                                onChange={(e) => handleSearchChange(filter, e.target.value)}
                            />
                            <div className="checkbox-list">
                                {filterOptions[filter].filter(option =>
                                    option.toLowerCase().includes(searchTerms[filter].toLowerCase())
                                ).map(option => (
                                    <label key={option}>
                                        <input
                                            type="checkbox"
                                            checked={filters[filter].includes(option)}
                                            onChange={() => {
                                                const newValues = filters[filter].includes(option)
                                                    ? filters[filter].filter(item => item !== option)
                                                    : [...filters[filter], option];
                                                handleFilterChange(filter, newValues);
                                            }}
                                        />
                                        {option}
                                    </label>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
            <div className="dashboard-content">
                <Routes>
                    <Route path="table" element={<TableComponent filters={filters} />} />
                    <Route path="chart" element={<ChartPage filters={filters} />} />
                    <Route path="map" element={<MapPage filters={filters} />} />
                </Routes>
            </div>
        </div>
    );
}

export default Dashboard;
