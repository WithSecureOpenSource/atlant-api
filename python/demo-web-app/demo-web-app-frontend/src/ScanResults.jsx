import React from "react";

function getVerdictClassName(verdict) {
  switch (verdict) {
    case "content_required":
      return "list-group-item-warning";
    case "clean":
    case "whitelisted":
      return "list-group-item-success";
    default:
      return "list-group-item-danger";
  }
}

export default function ScanResults({ results }) {
  if (!results) {
    return null;
  }

  const { verdict, infection_name: infectionName, categories } = results;
  const verdictCategory = getVerdictClassName(verdict);

  let categoryList = null;
  if (categories !== undefined && categories.length > 0) {
    categoryList = categories.map((category, i) => (
      <span key={i}>{category}</span>
    ));
  }

  return (
    <div className="card my-3">
      <div className="list-group list-group-flush">
        <div className={`list-group-item ${verdictCategory}`}>
          <h6>Verdict</h6>
          {verdict}
        </div>
        {infectionName && (
          <div className={`list-group-item ${verdictCategory}`}>
            <h6>Infection Name</h6>
            {infectionName}
          </div>
        )}
        {categoryList && (
          <div className={`list-group-item ${verdictCategory}`}>
            <h6>Categories</h6>
            {categoryList}
          </div>
        )}
      </div>
    </div>
  );
}
