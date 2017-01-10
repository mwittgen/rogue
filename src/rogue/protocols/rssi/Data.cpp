/**
 *-----------------------------------------------------------------------------
 * Title      : RSII Data Class
 * ----------------------------------------------------------------------------
 * File       : Data.h
 * Created    : 2017-01-07
 * Last update: 2017-01-07
 * ----------------------------------------------------------------------------
 * Description:
 * RSSI Data
 * ----------------------------------------------------------------------------
 * This file is part of the rogue software platform. It is subject to 
 * the license terms in the LICENSE.txt file found in the top-level directory 
 * of this distribution and at: 
 *    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
 * No part of the rogue software platform, including this file, may be 
 * copied, modified, propagated, or distributed except according to the terms 
 * contained in the LICENSE.txt file.
 * ----------------------------------------------------------------------------
**/
#include <rogue/protocols/rssi/Data.h>
#include <boost/make_shared.hpp>
#include <rogue/common.h>
#include <stdint.h>
#include <rogue/interfaces/stream/Buffer.h>

namespace rpr = rogue::protocols::rssi;
namespace ris = rogue::interfaces::stream;
namespace bp  = boost::python;

//! Class creation
rpr::DataPtr rpr::Data::create (ris::FramePtr frame) {
   rpr::DataPtr r = boost::make_shared<rpr::Data>(frame);
   return(r);
}

//! Creator
rpr::Data::Data ( ris::FramePtr frame ) : Header(frame) { }

//! Destructor
rpr::Data::~Data() { }

//! Return pointer to data
uint8_t * rpr::Data::getData() {
   return(buff_->getPayloadData());
}

//! Get data size
uint32_t rpr::Data::getDataSize() {
   return(buff_->getPayload());
}

