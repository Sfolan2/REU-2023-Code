/*
 * Artery V2X Simulation Framework
 * Copyright 2016-2017 Raphael Riebl
 * Licensed under GPLv2, see COPYING file for detailed license and warranty terms.
 */

#include "artery/application/Asn1PacketVisitor.h"
#include "artery/application/DenmObject.h"
#include "artery/application/DenService.h"
#include "artery/application/Timer.h"
#include "artery/application/StoryboardSignal.h"
#include "artery/application/VehicleDataProvider.h"
#include "artery/utility/FilterRules.h"
#include <omnetpp/checkandcast.h>
#include <omnetpp/ccomponenttype.h>
#include <omnetpp/cxmlelement.h>
#include <vanetza/asn1/denm.hpp>
#include <vanetza/btp/ports.hpp>
#include <vanetza/facilities/cam_functions.hpp>
#include <vanetza/facilities/denm_functions.hpp>
#include <iostream>
#include <sys/socket.h>
#include <arpa/inet.h>
#include "artery/traci/VehicleController.h"

//extern asn_TYPE_descriptor_t asn_DEF_CAM; 
#define SocketPORT 65432

int mypythonsocket1 = 0; 

using namespace omnetpp;

namespace artery
{

Define_Module(DenService)

static const simsignal_t denmReceivedSignal = cComponent::registerSignal("DenmReceived");
static const simsignal_t denmSentSignal = cComponent::registerSignal("DenmSent");
static const simsignal_t storyboardSignal = cComponent::registerSignal("StoryboardSignal");

DenService::DenService() :
    mTimer(nullptr), mSequenceNumber(0)
{
}

void DenService::initialize()
{
    printf("Correct Artery for DENMs\n");
    ItsG5BaseService::initialize();
    //mVehicleDataProvider = &getFacilities().get_const<VehicleDataProvider>(); //Added
    mTimer = &getFacilities().get_const<Timer>();
    mMemory.reset(new artery::den::Memory(*mTimer));

    subscribe(storyboardSignal);
    initUseCases();
}

void DenService::initUseCases()
{
    omnetpp::cXMLElement* useCases = par("useCases").xmlValue();
    for (omnetpp::cXMLElement* useCaseElement : useCases->getChildrenByTagName("usecase")) {
        omnetpp::cModuleType* useCaseType = omnetpp::cModuleType::get(useCaseElement->getAttribute("type"));
        omnetpp::cXMLElement* filter = useCaseElement->getFirstChildWithTag("filters");

        bool useCaseApplicable = true;
        if (filter) {
            artery::FilterRules rules(getRNG(0), getFacilities().get_const<artery::Identity>());
            useCaseApplicable = rules.applyFilterConfig(*filter);
        }

        if (useCaseApplicable) {
            const char* useCaseName = useCaseElement->getAttribute("name") ?
                useCaseElement->getAttribute("name") : useCaseType->getName();
            omnetpp::cModule* module = useCaseType->create(useCaseName, this);
            // do not call initialize here! omnetpp::cModule initializes submodules on its own!
            module->buildInside();
            den::UseCase* useCase = dynamic_cast<den::UseCase*>(module);
            if (useCase) {
                mUseCases.push_front(useCase);
            }
        }
    }
}

void DenService::receiveSignal(cComponent*, simsignal_t signal, cObject* obj, cObject*)
{
    if (signal == storyboardSignal) {
        StoryboardSignal* storyboardSignalObj = check_and_cast<StoryboardSignal*>(obj);
        for (auto use_case : mUseCases) {
            use_case->handleStoryboardTrigger(*storyboardSignalObj);
        }
    }
}

//////////////////////////New Code////////////////////////////////////////////////
//////////////////////////Hopefully I know what I am doing////////////////////////
int sendSocketDenmToPython(int port, const vanetza::asn1::Denm* denm)
{

    struct sockaddr_in serv_addr;
    if (mypythonsocket1==0)
	{	
		if ((mypythonsocket1 = socket(AF_INET, SOCK_STREAM, 0)) < 0)
		{
			printf("\n Socket creation error \n");
			std::cout<<"\n Socket creation error \n";
			return -1;
		}
		
		serv_addr.sin_family = AF_INET;
		serv_addr.sin_port = htons(port);
		
		// Convert IPv4 and IPv6 addresses from text to binary form
		if(inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr)<=0) 
		{
			printf("\nInvalid address/ Address not supported \n");

			std::cout<<"\n Invalid address/ Address not supported \n";
			return -1;
		}
	
		if (connect(mypythonsocket1, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
		{
			printf("\nConnection Failed \n");
			std::cout<<"\n Connection Failed \n";
			close(mypythonsocket1);
			mypythonsocket1=0;
			return -1;
		}
	}
	// sending denm message to carla python socket server
	printf("Attempting to send DENMs\n");
	std::cout<<"Attempting to send DENMs\n";
	std::stringstream ss;
	
    	vanetza::facilities::print_indented_denm(ss,*denm,"",0);
    std::string myString = ss.str();
	char nstr[8]; 
	int n= myString.length();
	snprintf(nstr, 7,"%06d", n);
	send(mypythonsocket1 , nstr , 6 , 0 );
    send(mypythonsocket1 , myString.c_str() , n , 0 );

	return 0;



}
//////////////////////////////////////////////////////////////////////////////////////////

void DenService::indicate(const vanetza::btp::DataIndication& indication, std::unique_ptr<vanetza::UpPacket> packet)
{
    Asn1PacketVisitor<vanetza::asn1::Denm> visitor;
    const vanetza::asn1::Denm* denm = boost::apply_visitor(visitor, *packet);
    const auto egoStationID = getFacilities().get_const<VehicleDataProvider>().station_id();
    
    printf("Here");
    if (denm && (*denm)->header.stationID != egoStationID) {
    	printf("Here2\n");
        DenmObject obj = visitor.shared_wrapper;
        mMemory->received(obj);
        emit(denmReceivedSignal, &obj);

	sendSocketDenmToPython(SocketPORT,denm);
        for (auto use_case : mUseCases) {
            use_case->indicate(obj);
        }
    }
}

void DenService::trigger()
{
    mMemory->drop();

    for (auto use_case : mUseCases) {
        use_case->check();
    }
}

ActionID_t DenService::requestActionID()
{
    ActionID_t id;
    id.originatingStationID = getFacilities().get_const<VehicleDataProvider>().station_id();
    id.sequenceNumber = ++mSequenceNumber;
    return id;
}

const Timer* DenService::getTimer() const
{
    return mTimer;
}

std::shared_ptr<const den::Memory> DenService::getMemory() const
{
    return mMemory;
}

void DenService::sendDenm(vanetza::asn1::Denm&& message, vanetza::btp::DataRequestB& request)
{
    printf("Sending DENM\n");
    fillRequest(request);
    DenmObject obj { std::move(message) };
    emit(denmSentSignal, &obj);

    using namespace vanetza;
    using DenmConvertible = vanetza::convertible::byte_buffer_impl<vanetza::asn1::Denm>;
    std::unique_ptr<geonet::DownPacket> payload { new geonet::DownPacket };
    std::unique_ptr<vanetza::convertible::byte_buffer> denm { new DenmConvertible { obj.shared_ptr() } };
    payload->layer(OsiLayer::Application) = vanetza::ByteBufferConvertible { std::move(denm) };
    this->request(request, std::move(payload));
}

void DenService::fillRequest(vanetza::btp::DataRequestB& request)
{
    using namespace vanetza;

    request.destination_port = btp::ports::DENM;
    request.gn.its_aid = aid::DEN;
    request.gn.transport_type = geonet::TransportType::GBC;
    request.gn.communication_profile = geonet::CommunicationProfile::ITS_G5;
}

} // namespace artery
