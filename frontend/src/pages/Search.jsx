import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Search as SearchIcon } from "lucide-react";
import { api } from "../lib/api";
import Avatar from "../components/Avatar";

export default function Search() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Debounced search - waits for a pause in typing before hitting the API,
  // so we're not firing a request on every keystroke.
  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      return;
    }

    setLoading(true);
    const timer = setTimeout(() => {
      api.searchProfiles(trimmed)
        .then(setResults)
        .catch((e) => setError(e.message))
        .finally(() => setLoading(false));
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  return (
    <div>
      <div className="search-box">
        <SearchIcon size={18} className="search-icon" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by username or name"
          autoFocus
        />
      </div>

      {error && <p className="error-text">{error}</p>}

      {loading ? (
        <p className="empty-text">Searching...</p>
      ) : query.trim() === "" ? (
        <p className="empty-text">Find people by username or display name.</p>
      ) : results.length === 0 ? (
        <p className="empty-text">No one found for "{query}".</p>
      ) : (
        <ul className="search-results">
          {results.map((p) => (
            <li key={p.id}>
              <Link to={`/u/${p.username}`} className="search-result-row">
                <Avatar name={p.display_name} url={p.avatar_url} size={44} />
                <div>
                  <div className="search-result-name">{p.display_name}</div>
                  <div className="search-result-username">@{p.username}</div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
