/**
 *-----------------------------------------------------------------------------
 * Title         : SLAC Register Protocol (SRP) Bridge
 * ----------------------------------------------------------------------------
 * File          : Bridge.cpp
 * Author        : Ryan Herbst <rherbst@slac.stanford.edu>
 * Created       : 09/17/2016
 * Last update   : 09/17/2016
 *-----------------------------------------------------------------------------
 * Description :
 *    SRP protocol bridge
 *-----------------------------------------------------------------------------
 * This file is part of the rogue software platform. It is subject to 
 * the license terms in the LICENSE.txt file found in the top-level directory 
 * of this distribution and at: 
    * https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
 * No part of the rogue software platform, including this file, may be 
 * copied, modified, propagated, or distributed except according to the terms 
 * contained in the LICENSE.txt file.
 *-----------------------------------------------------------------------------
**/
#include <stdint.h>
#include <boost/thread.hpp>
#include <boost/make_shared.hpp>
#include <rogue/interfaces/stream/Master.h>
#include <rogue/interfaces/stream/Slave.h>
#include <rogue/interfaces/stream/Frame.h>
#include <rogue/interfaces/memory/Slave.h>
#include <rogue/interfaces/memory/Block.h>
#include <rogue/protocols/srp/Bridge.h>
#include <rogue/protocols/srp/Transaction.h>
#include <rogue/protocols/srp/TransactionV0.h>
#include <rogue/protocols/srp/TransactionV3.h>

namespace bp = boost::python;
namespace rps = rogue::protocols::srp;
namespace rim = rogue::interfaces::memory;
namespace ris = rogue::interfaces::stream;

//! Class creation
rps::BridgePtr rps::Bridge::create (uint32_t version) {
   rps::BridgePtr p = boost::make_shared<rps::Bridge>(version);
   return(p);
}

//! Setup class in python
void rps::Bridge::setup_python() {

   bp::class_<rps::Bridge, bp::bases<ris::Master,ris::Slave,rim::Slave>, 
              rps::BridgePtr, boost::noncopyable >("Bridge",bp::init<uint32_t>())
      .def("create",         &rps::Bridge::create)
      .staticmethod("create")
   ;

}

//! Creator with version constant
rps::Bridge::Bridge(uint32_t version) {
   version_ = version;
}

//! Deconstructor
rps::Bridge::~Bridge() {}

//! Post a transaction
void rps::Bridge::doTransaction(bool write, bool posted, rim::BlockPtr block) {
   uint32_t size;
   rps::TransactionPtr tp;
   ris::FramePtr frame;

   boost::lock_guard<boost::mutex> lock(tranMapMtx_);

   if ( tranMap_.find(block->getIndex()) != tranMap_.end() ) 
      tp = tranMap_[block->getIndex()];
   else {

      if ( version_ == 0 )
         tp = rps::TransactionV0::create(block);
      else if ( version_ == 3 )
         tp = rps::TransactionV3::create(block);
      else
         tp = rps::Transaction::create(block);

      tranMap_[block->getIndex()] = tp;
   }

   size = tp->init(write,posted);
   frame = reqFrame(size,true);
   if ( tp->genFrame(frame) ) sendFrame(frame);
}

//! Accept a frame from master
void rps::Bridge::acceptFrame ( ris::FramePtr frame ) {
   rps::TransactionPtr tp;
   uint32_t index;

   if ( version_ == 0 )
      index = rps::TransactionV0::extractTid(frame);
   else if ( version_ == 3 )
      index = rps::TransactionV3::extractTid(frame);
   else
      index = rps::Transaction::extractTid(frame);

   boost::lock_guard<boost::mutex> lock(tranMapMtx_);

   if ( tranMap_.find(index) != tranMap_.end() ) {
      tp = tranMap_[index];
   } else {
      printf("Matching TID not found %i\n",index);
      return;
   }

   tp->recvFrame(frame);
}
