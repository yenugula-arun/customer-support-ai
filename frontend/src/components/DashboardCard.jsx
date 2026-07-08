function DashboardCard({
    title,
    value,
    className
}) {

    return (

        <div className={`rounded-xl shadow-lg p-6 text-white ${className}`}>

            <h3 className="text-lg font-semibold">
                {title}
            </h3>

            <p className="text-4xl font-bold mt-4">
                {value}
            </p>

        </div>

    );

}

export default DashboardCard;