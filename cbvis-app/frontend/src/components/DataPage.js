import React from 'react';
import { Link } from 'react-router-dom';
import TableComponent from './TableComponent';

const DataPage = () => {
    return (
        <div>
            <div className="data-page-menu">
                <Link to="/data/table">Table</Link>
                <Link to="/data/chart">Chart (Coming Soon)</Link>
                <Link to="/data/map">Map (Coming Soon)</Link>
            </div>
            <TableComponent />
        </div>
    );
}

export default DataPage;
