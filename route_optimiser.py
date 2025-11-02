"""
route_optimiser.py
------------------
Helper functions for summarizing route data and generating clean responses
for the Smart Route Optimization Flask application.
"""

def format_time(minutes):
    """
    Convert time in minutes to a readable 'X hr Y min' format.
    """
    if minutes < 60:
        return f"{round(minutes)} min"
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours} hr {mins} min" if mins else f"{hours} hr"


def summarize_route(optimized_path, total_distance, estimated_time):
    """
    Generate a summary dictionary of the optimized route.

    Parameters:
        optimized_path (list): List of locations in the optimized order.
        total_distance (float): Total route distance in kilometers.
        estimated_time (float): Estimated travel time in minutes.

    Returns:
        dict: Summary ready for JSON response to frontend.
    """
    if not optimized_path:
        return {"error": "No optimized route found"}

    formatted_time = format_time(estimated_time)

    summary = {
        "optimized_path": optimized_path,
        "total_distance": round(total_distance, 2),
        "estimated_time": round(estimated_time, 2),
        "formatted_time": formatted_time,
        "summary_message": (
            f"Optimized route covers {round(total_distance, 2)} km "
            f"and will take approximately {formatted_time}."
        )
    }

    return summary


def summarize_error(message):
    """
    Create a consistent error response dictionary.
    """
    return {"error": message}
