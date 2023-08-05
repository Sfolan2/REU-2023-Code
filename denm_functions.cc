/*
I don't really know C++ that well, so let's see if this works
Trying to emulate cam_functions.cc from VANETZA
*/


#include <vanetza/asn1/denm.hpp>
#include <vanetza/facilities/denm_functions.hpp>
#include <vanetza/facilities/path_history.hpp>
#include <vanetza/geonet/areas.hpp>
#include <boost/algorithm/clamp.hpp>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <boost/math/constants/constants.hpp>
#include <boost/units/cmath.hpp>
#include <boost/units/systems/si/prefixes.hpp>
#include <boost/units/systems/angle/degrees.hpp>
#include <algorithm>
#include <limits>
#undef min

namespace vanetza
{
namespace facilities
{

void print_indented_denm(std::ostream& os, const asn1::Denm& message, const std::string& indent, unsigned level)
{
    auto prefix = [&](const char* field) -> std::ostream& {
        for (unsigned i = 0; i < level; ++i) {
            os << indent;
        }
        os << field << ": ";
        return os;
    };

    const ItsPduHeader_t& header = message->header;
    prefix("ITS PDU Header") << "\n";
    ++level;
    prefix("Protocol Version") << header.protocolVersion << "\n";
    prefix("Message ID") << header.messageID << "\n";
    prefix("Station ID") << header.stationID << "\n";
    --level;

    const ManagementContainer_t& management = message->denm.management;
    prefix("Management") << "\n";
    ++level;
    prefix("Originating Station ID") << management.actionID.originatingStationID << "\n";
    prefix("Sequence Number") << management.actionID.sequenceNumber << "\n";
    prefix("Alitude [Confidence]") << management.eventPosition.altitude.altitudeValue << "[" << management.eventPosition.altitude.altitudeConfidence << "]" << "\n";
    prefix("Longitude") << management.eventPosition.longitude << "\n";
    prefix("Latitude") << management.eventPosition.latitude << "\n";
    prefix("Semi Major Orientation") << management.eventPosition.positionConfidenceEllipse.semiMajorOrientation << "\n";
    prefix("Semi Major Confidence") << management.eventPosition.positionConfidenceEllipse.semiMajorConfidence << "\n";
    prefix("Semi Minor Confidence") << management.eventPosition.positionConfidenceEllipse.semiMinorConfidence << "\n";
    // Also for all attacks but not in Skeleton
    prefix("Relevance Distance") << *management.relevanceDistance << "\n"; // Should be a number which can be converted into an actual number with the VANETZA repo
    prefix("Relevance Traffic Detection") << *management.relevanceTrafficDirection << "\n";
    prefix("Validity Duration") << *management.validityDuration << "\n"
    --level;

    const LocationContainer_t& location = message->denm.location; // With or without _t?
    prefix("Location") << "\n";
    ++level;
    prefix("Speed") << location->eventSpeed->speedValue << "\n";
    prefix("Speed Confidence") << location->eventSpeed->speedConfidence << "\n";
    prefix("Heading [Confidence]") << location->eventPositionHeading->headingValue << "[" << location->eventPositionHeading->headingConfidence << "]" << "\n";
    --level;

    const Situation_Container_t& situation = message->denm.situation;
    // Also for all attacks but not in Skeleton
    prefix("Situation") << "\n";
    ++level;
    prefix("Information Quality") << situation->informationQuality << "\n";
    prefix("Cause Code") << situation->eventType.causeCode << "\n";
    prefix("Sub Cause Code") << situation->eventType.subCauseCode "\n";
    --level;
}

} // namespace facilities
} // namsepace vanetza
