function SearchBar({

  value,

  onChange

}) {

  return (

    <input

      type="text"

      value={value}

      onChange={(e)=>onChange(e.target.value)}

      placeholder="Search tickets..."

      className="w-full border rounded-xl px-5 py-3 mb-6"

    />

  );

}

export default SearchBar;