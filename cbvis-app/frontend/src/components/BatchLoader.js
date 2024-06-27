import React, { useState, useEffect, useCallback, useRef } from 'react';
import axiosInstance from './axiosInstance';
import './BatchLoader.css';

const BatchLoader = ({ onSeriesNamesLoaded, onSeriesSelected, batchSize = 20 }) => {
    const [seriesNames, setSeriesNames] = useState([]);
    const [filteredSeriesNames, setFilteredSeriesNames] = useState([]);
    const [selectedSeriesIds, setSelectedSeriesIds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [offset, setOffset] = useState(0);
    const [searchTerm, setSearchTerm] = useState('');
    const [collapsed, setCollapsed] = useState(false);
    const dropdownRef = useRef(null);
    const observerRef = useRef(null);

    const loadMoreSeriesNames = useCallback(async () => {
        setLoading(true);
        try {
            const response = await axiosInstance.get('/api/series_names', { params: { offset, limit: batchSize } });
            const newSeriesNames = response.data.series_names;
            setSeriesNames(prevNames => [...prevNames, ...newSeriesNames]);
            setFilteredSeriesNames(prevNames => [...prevNames, ...newSeriesNames]);
            setOffset(prevOffset => prevOffset + batchSize);
            onSeriesNamesLoaded(newSeriesNames);
        } catch (err) {
            setError('Error loading series names');
            console.error(err);
        } finally {
            setLoading(false);
        }
    }, [offset, batchSize, onSeriesNamesLoaded]);

    useEffect(() => {
        loadMoreSeriesNames();
    }, []); // Run only once on component mount

    useEffect(() => {
        if (searchTerm) {
            const filtered = seriesNames.filter(name =>
                name.series_name.toLowerCase().includes(searchTerm.toLowerCase())
            );
            setFilteredSeriesNames(filtered);
        } else {
            setFilteredSeriesNames(seriesNames);
        }
    }, [searchTerm, seriesNames]);

    const handleOutsideClick = (event) => {
        if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
            setFilteredSeriesNames([]);
        }
    };

    useEffect(() => {
        document.addEventListener('mousedown', handleOutsideClick);
        return () => {
            document.removeEventListener('mousedown', handleOutsideClick);
        };
    }, []);

    const handleSeriesClick = (seriesId) => {
        setSelectedSeriesIds(prevIds => {
            if (prevIds.includes(seriesId)) {
                return prevIds.filter(id => id !== seriesId);
            } else {
                return [...prevIds, seriesId];
            }
        });
    };

    const handleAddSelectedSeries = () => {
        selectedSeriesIds.forEach(seriesId => onSeriesSelected(seriesId));
        setSelectedSeriesIds([]);
    };

    const toggleCollapse = () => {
        setCollapsed(!collapsed);
    };

    useEffect(() => {
        const observer = new IntersectionObserver(entries => {
            if (entries[0].isIntersecting && !loading) {
                loadMoreSeriesNames();
            }
        }, {
            root: dropdownRef.current,
            rootMargin: '0px',
            threshold: 1.0
        });

        if (observerRef.current) {
            observer.observe(observerRef.current);
        }

        return () => {
            if (observerRef.current) {
                observer.unobserve(observerRef.current);
            }
        };
    }, [loading, loadMoreSeriesNames]);

    return (
        <div ref={dropdownRef} className={`batch-loader ${collapsed ? 'collapsed' : ''}`}>
            <div className="header">
                <h2>Search Series</h2>
                <button onClick={toggleCollapse}>{collapsed ? '▼' : '▲'}</button>
            </div>
            {!collapsed && (
                <div className="content">
                    {error && <p>{error}</p>}
                    <div className="search-bar-container">
                        <input
                            type="text"
                            placeholder="Search series"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <button onClick={handleAddSelectedSeries} disabled={selectedSeriesIds.length === 0}>
                            Add Selected Series
                        </button>
                    </div>
                    <div className="dropdown-menu">
                        <ul>
                            {filteredSeriesNames.map((series, index) => (
                                <li key={index} onClick={() => handleSeriesClick(series.series_id)}>
                                    <div className="series-name">{series.series_name}</div>
                                    <div className="series-details">
                                        <small>ID: {series.series_id}</small><br />
                                        <small>Frequency: {series.frequency}</small><br />
                                        <small>Units: {series.units}</small><br />
                                        <small>Source: {series.source_name}</small>
                                    </div>
                                </li>
                            ))}
                        </ul>
                        <div ref={observerRef} />
                    </div>
                </div>
            )}
        </div>
    );
};

export default BatchLoader;
