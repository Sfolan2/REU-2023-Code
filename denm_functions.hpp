#ifndef DENM_FUNCTIONS_HPP_PUFKBEM8
#define DENM_FUNCTIONS_HPP_PUFKBEM8

namespace vanetza
{

// forward declaration of CAM message wrapper
namespace asn1 { class Denm; }

namespace facilities
{
class PathHistory;

void print_indented_denm(std::ostream& os, const asn1::Denm& message, const std::string& indent, unsigned level);

} // facilities
} // vanetza

#endif /*DENM_FUNCTIONS_HPP_PUFKBEM8*/
