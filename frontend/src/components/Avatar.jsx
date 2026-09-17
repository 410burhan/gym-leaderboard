function initials(name) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join("");
}

export default function Avatar({ name, url, size = 40 }) {
  const style = { width: size, height: size, fontSize: size * 0.4 };

  if (url) {
    return <img src={url} alt={name} className="avatar" style={style} />;
  }

  return (
    <div className="avatar avatar-fallback" style={style}>
      {initials(name || "?")}
    </div>
  );
}
